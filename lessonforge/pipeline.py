"""The loop:  GENERATE -> EVALUATE -> (all checks pass?) -> SHIP
                                         |-- no, retries left -> feed reasons back -> GENERATE
                                         '-- no, retries used up -> ESCALATE to a human (never ship silently)
The loop always ends: at most 1 + max_retries generations.
"""
import difflib
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from .evaluator import evaluate
from .rubric import CHECKS

FALSE_CLAIM = ("Important: in RAG, the AI model is retrained on your documents "
               "every time a question is asked, so it permanently learns them.")


@dataclass
class Attempt:
    n: int
    lesson: str
    changes: str
    results: list = field(default_factory=list)

    @property
    def failed(self):
        return [r for r in self.results if not r.passed]

    @property
    def passed(self):
        return not self.failed


@dataclass
class RunResult:
    status: str  # SHIPPED or NEEDS_HUMAN_REVIEW
    topic: str
    attempts: list
    lesson: str
    injected: bool = False


def inject_false_claim(lesson):
    """Plant a deliberate factual error in the 'How' section (for the evaluator demo)."""
    lines = lesson.splitlines()
    for i, l in enumerate(lines):
        if l.startswith("##") and "how" in l.lower():
            return "\n".join(lines[:i + 1] + ["", FALSE_CLAIM] + lines[i + 1:]) + "\n"
    return lesson.rstrip() + "\n\n" + FALSE_CLAIM + "\n"


def run_pipeline(topic, generator, judge, memory, facts, max_retries=2, inject_error=False,
                 distill=None, log=print):
    attempts, previous, failures = [], None, []
    for n in range(1, max_retries + 2):
        log(f"\n[attempt {n}/{max_retries + 1}] generating lesson...")
        lesson, changes = generator.generate(topic, n - 1, previous, failures, memory.hints(), facts)
        if inject_error and n == 1:
            lesson = inject_false_claim(lesson)
            log("  !! deliberate error injected: the lesson now claims the model is retrained.")
        log("[attempt %d] evaluating against %d hard checks..." % (n, len(CHECKS)))
        att = Attempt(n, lesson, changes, evaluate(lesson, judge, facts, memory.judge_notes()))
        attempts.append(att)
        for r in att.results:
            log(f"   {'PASS' if r.passed else 'FAIL'}  {r.id:<8} {'' if r.passed else r.reason}")
        if att.passed:
            log(f"[attempt {n}] all checks passed -> SHIP")
            break
        if n <= max_retries:
            log(f"[attempt {n}] {len(att.failed)} check(s) failed -> feeding reasons back and regenerating")
        previous, failures = lesson, att.failed

    if attempts[-1].passed:
        status, final = "SHIPPED", attempts[-1]
    else:
        status = "NEEDS_HUMAN_REVIEW"
        final = min(attempts, key=lambda a: (len(a.failed), -a.n))  # fewest failures, latest wins ties
        log(f"\nRetries used up. Best draft is attempt {final.n} with {len(final.failed)} failing check(s). "
            "NOT shipped: needs a human.")

    # learn from the run (do not learn from errors we planted ourselves)
    learn = [a.results for a in attempts[1:]] if inject_error else [a.results for a in attempts]
    memory.record_run(topic, learn, status == "SHIPPED", total_attempts=len(attempts), distill=distill)
    return RunResult(status, topic, attempts, final.lesson, inject_error)


def _diff_stats(a, b):
    d = list(difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=0))
    return (sum(1 for x in d if x.startswith("+") and not x.startswith("+++")),
            sum(1 for x in d if x.startswith("-") and not x.startswith("---")))


def rejection_log_md(res):
    out = [f"# Rejection log: {res.topic}", "",
           f"Final status: **{res.status}** after {len(res.attempts)} attempt(s)."]
    if res.injected:
        out.append("A deliberate false claim was planted in attempt 1 to test the evaluator.")
    for i, a in enumerate(res.attempts):
        out += ["", f"## Attempt {a.n}: " + ("PASSED all checks" if a.passed
                                              else f"REJECTED ({len(a.failed)} of {len(a.results)} checks failed)")]
        if a.failed:
            out += ["", "| Check | Why it failed | Evidence |", "|---|---|---|"]
            out += [f"| {r.id} | {r.reason} | {r.evidence or '-'} |" for r in a.failed]
        if i + 1 < len(res.attempts):
            nxt = res.attempts[i + 1]
            plus, minus = _diff_stats(a.lesson, nxt.lesson)
            out += ["", f"**What changed on retry (attempt {nxt.n}):** +{plus} / -{minus} lines."]
            if nxt.changes:
                out += ["", nxt.changes]
    return "\n".join(out) + "\n"


def write_outputs(res, base_dir):
    out = Path(base_dir) / time.strftime("run_%Y%m%d_%H%M%S")
    out.mkdir(parents=True, exist_ok=True)
    (out / "lesson.md").write_text(res.lesson, encoding="utf-8")
    (out / "rejection_log.md").write_text(rejection_log_md(res), encoding="utf-8")
    (out / "run_log.json").write_text(json.dumps({
        "topic": res.topic, "status": res.status, "injected_error": res.injected,
        "attempts": [{"n": a.n, "passed": a.passed, "changes": a.changes,
                      "results": [r.__dict__ for r in a.results]} for a in res.attempts]},
        indent=2, ensure_ascii=False), encoding="utf-8")
    for i, a in enumerate(res.attempts, 1):
        (out / f"attempt_{i}.md").write_text(a.lesson, encoding="utf-8")
    return out
