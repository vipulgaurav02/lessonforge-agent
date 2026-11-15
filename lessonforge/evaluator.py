"""Evaluator: hard pass/fail verdicts for every rubric check.

Three parts:
  1. deterministic_checks()  - Python measures what can be measured (length, structure).
  2. LLMJudge                - a SEPARATE model call judges meaning (accuracy, jargon, examples).
                               It must quote evidence, and it FAILS CLOSED: a missing or broken
                               verdict counts as a fail, never as a pass.
  3. HeuristicJudge          - a rule-based stand-in used for offline demos and CI tests.
                               It is NOT a substitute for the LLM judge.
"""
import json
import re
from dataclasses import dataclass

from .rubric import BY_ID, CHECKS

WORD_RE = re.compile(r"[A-Za-z0-9'’-]+")
HEADING_KEYS = ["what", "why", "how", "example", "recap"]


@dataclass
class CheckResult:
    id: str
    passed: bool
    reason: str
    evidence: str = ""


# ---------- text helpers ----------

def _clean(s: str) -> str:
    return re.sub(r"[*_`>]", "", s)


def sentences(text: str) -> list:
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        s = re.sub(r"^(\d+\.|[-•])\s+", "", _clean(s))
        out.extend(p.strip() for p in re.split(r"(?<=[.!?])\s+", s) if WORD_RE.search(p))
    return out


def n_words(s: str) -> int:
    return len(WORD_RE.findall(s))


def headings(text: str) -> list:
    return [l[3:].strip().lower() for l in text.splitlines() if l.startswith("## ")]


def heading_order_ok(text: str) -> bool:
    heads, pos = headings(text), -1
    for key in HEADING_KEYS:
        idx = next((i for i, h in enumerate(heads) if i > pos and key in h), None)
        if idx is None:
            return False
        pos = idx
    return True


def section(text: str, key: str) -> str:
    """Text of the first '## ' section whose heading contains `key`."""
    parts = re.split(r"^## ", text, flags=re.M)
    for p in parts[1:]:
        if key in p.splitlines()[0].lower():
            return "\n".join(p.splitlines()[1:])
    return ""


# ---------- 1. deterministic checks ----------

def deterministic_checks(lesson: str) -> list:
    sents = sentences(lesson)
    lens = [n_words(s) for s in sents] or [0]
    avg = sum(lens) / len(lens)
    longest = max(sents, key=n_words) if sents else ""
    total_words = n_words(_clean(lesson))
    questions = len(re.findall(r"^\s*\d+\.\s+.*\?", section(lesson, "check yourself"), re.M))

    r = []
    r.append(CheckResult("LANG1", avg <= 15,
                         f"Average sentence length is {avg:.1f} words (limit 15)."))
    r.append(CheckResult("LANG2", max(lens) <= 25,
                         f"Longest sentence has {max(lens)} words (limit 25).",
                         " ".join(longest.split()[:12]) if max(lens) > 25 else ""))
    problems = []
    if not 500 <= total_words <= 1000:
        problems.append(f"word count is {total_words} (needs 500-1000)")
    if not heading_order_ok(lesson):
        problems.append("the five headings What/Why/How/Example/Recap are missing or out of order")
    if questions != 3:
        problems.append(f"'Check yourself' has {questions} numbered questions (needs exactly 3)")
    r.append(CheckResult("STRUCT1", not problems,
                         "Structure is correct." if not problems else "; ".join(problems) + "."))
    return r


# ---------- 2. LLM judge ----------

JUDGE_SYSTEM = """You are a strict reviewer of beginner lessons. You never write or fix lessons.
For each check give PASS or FAIL. No partial credit. If you are unsure, FAIL.
The learner: a 12th-grade graduate from India, non-English-medium school, limited English, knows nothing about AI.
Judge accuracy ONLY against the fact sheet.
Return ONLY JSON, nothing else, in this shape:
{"checks": [{"id": "ACC1", "pass": true, "reason": "one short sentence", "evidence": "quote of at most 12 words from the lesson, or empty"}]}
Include every check id exactly once."""


class LLMJudge:
    def __init__(self, llm):
        self.llm = llm

    def _prompt(self, lesson, facts, notes):
        lines = []
        for c in CHECKS:
            if c.kind != "llm":
                continue
            extra = ""
            if notes.get(c.id):
                extra = "\n   Known failure patterns to look for: " + " | ".join(notes[c.id])
            lines.append(f"- {c.id}: {c.question}{extra}")
        return (f"FACT SHEET:\n{facts}\n\nCHECKS:\n" + "\n".join(lines) +
                f"\n\nLESSON TO REVIEW:\n<lesson>\n{lesson}\n</lesson>")

    @staticmethod
    def _parse(raw, wanted):
        data = json.loads(re.search(r"\{.*\}", raw, re.S).group(0))
        out = {}
        for item in data["checks"]:
            if item.get("id") in wanted and isinstance(item.get("pass"), bool):
                out[item["id"]] = CheckResult(item["id"], item["pass"],
                                              str(item.get("reason", "")), str(item.get("evidence", "")))
        return out

    def judge(self, lesson, facts, notes=None):
        wanted = [c.id for c in CHECKS if c.kind == "llm"]
        got = {}
        for _ in range(2):  # one retry if the judge returns broken JSON
            try:
                raw = self.llm.complete(JUDGE_SYSTEM, self._prompt(lesson, facts, notes or {}),
                                        temperature=0, max_tokens=2500)
                got = self._parse(raw, wanted)
                if len(got) == len(wanted):
                    break
            except Exception:
                got = {}
        return {i: got.get(i) or CheckResult(i, False, "Judge gave no valid verdict (fail-closed).")
                for i in wanted}


# ---------- 3. offline heuristic judge ----------

JARGON = ["chatbot", "LLM", "chunk", "embedding", "vector database", "hallucination"]
DEFINE_MARKERS = ["means", " is a ", " is an ", " is the ", "is called", "called a", "called an",
                  "stands for", "are called"]
IDIOMS = ["piece of cake", "under the hood", "out of the box", "bottom line", "tip of the iceberg",
          "at the end of the day", "game changer", "a no-brainer", "rule of thumb", "ballpark"]
NEGATIONS = ["not", "no ", "never", "nobody", "without", "n't", "nothing"]
CHANGE_MODEL = re.compile(r"retrain|re-train|fine-tun|model weights|updates? the model|model is updated", re.I)
OVERCLAIM = re.compile(r"never (makes?|gives?) (a )?(mistake|wrong)|always (correct|right|accurate)|100 ?%|"
                       r"removes? every mistake", re.I)


class HeuristicJudge:
    """Rule-based judge for offline demos and tests. Cruder than the LLM judge by design."""

    def judge(self, lesson, facts=None, notes=None):
        low = lesson.lower()
        sents = sentences(lesson)
        res = {}

        def put(i, ok, why, ev=""):
            res[i] = CheckResult(i, ok, why, ev)

        bad = next((s for s in sents if CHANGE_MODEL.search(s) and not any(n in s.lower() for n in NEGATIONS)), "")
        put("ACC2", not bad, "No claim that the model is retrained or changed." if not bad
            else "Says or implies the model is retrained/updated, which contradicts fact F8.", " ".join(bad.split()[:12]))
        over = next((s for s in sents if OVERCLAIM.search(s) and not any(n in s.lower() for n in NEGATIONS)), "")
        put("ACC1", not over, "No overclaims found." if not over else "Overclaims that RAG is perfect.",
            " ".join(over.split()[:12]))

        hit = next((i for i in IDIOMS if i in low), "")
        put("LANG3", not hit, "No idioms found." if not hit else f"Uses the idiom '{hit}'.", hit)

        unexplained = []
        for term in JARGON:
            for k, s in enumerate(sents):
                if re.search(rf"\b{re.escape(term)}s?\b", s, re.I):
                    window = " ".join(sents[k:k + 3]).lower()
                    if not any(m in window for m in DEFINE_MARKERS):
                        unexplained.append(term)
                    break
        put("JAR1", not unexplained, "Every jargon term is explained at first use." if not unexplained
            else "Used without explanation: " + ", ".join(unexplained) + ".", ", ".join(unexplained))

        put("EX1", bool(re.search(r"open-book|closed-book|library|imagine", low)),
            "Has an everyday analogy." if re.search(r"open-book|closed-book|library|imagine", low)
            else "No everyday analogy found.")
        ex = "question:" in low and "without rag" in low and "with rag" in low
        put("EX2", ex, "Has a worked example." if ex else "No worked example with and without RAG.")
        c1 = "retrieval-augmented generation" in low and bool(re.search(r"\bRAG is\b", lesson))
        put("COV1", c1, "Explains what RAG is." if c1 else "Does not explain what RAG is or its full name.")
        probs = sum(bool(re.search(p, low)) for p in [r"old|outdated|frozen|stops learning", r"private", r"hallucinat|mistake"])
        put("COV2", probs >= 2, f"Names {probs} problems RAG helps with." )
        how = section(lesson, "how").lower()
        pos = [how.find(k) for k in ("retriev", "augment", "generat")]
        put("COV3", all(p >= 0 for p in pos) and pos == sorted(pos),
            "Steps appear in order." if all(p >= 0 for p in pos) and pos == sorted(pos)
            else "Retrieve/augment/generate steps missing or out of order.")
        before_how = low.split("## 3")[0] if "## 3" in low else low
        fwd = [t for t in ("embedding", "vector database") if t in before_how]
        flow = heading_order_ok(lesson) and not fwd
        put("FLOW1", flow, "Order is What, Why, How, Example, Recap with no forward references." if flow
            else "Headings out of order or a technical term is used before the How section.")
        return res


def evaluate(lesson, judge, facts, notes=None):
    """Return one CheckResult per rubric check, in rubric order."""
    code = {r.id: r for r in deterministic_checks(lesson)}
    llm = judge.judge(lesson, facts, notes or {})
    return [code[c.id] if c.id in code else llm[c.id] for c in CHECKS]
