"""Command line.
  python -m lessonforge run --topic "Introduction to RAG" [--offline] [--inject-error] [--max-retries 2]
  python -m lessonforge feedback "text"     # teach the system from a human note
  python -m lessonforge memory              # see what it has learned
"""
import argparse
import json
from pathlib import Path

from .evaluator import HeuristicJudge, LLMJudge
from .generator import FixtureGenerator, LLMGenerator
from .memory import Memory
from .pipeline import run_pipeline, write_outputs
from .rubric import BY_ID

ROOT = Path(__file__).resolve().parent.parent


def _make_distill(llm):
    def distill(check_id, reasons):
        c = BY_ID[check_id]
        prompt = (f"A lesson keeps failing this check: {c.question}\nRecent failure reasons:\n- " +
                  "\n- ".join(reasons) +
                  "\nWrite ONE short imperative rule (max 25 words) that would help a lesson writer avoid this. "
                  "Output only the rule.")
        return llm.complete("You write short, concrete writing rules.", prompt, temperature=0, max_tokens=80).strip()
    return distill


def main(argv=None):
    ap = argparse.ArgumentParser(prog="lessonforge")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--topic", default="Introduction to RAG")
    r.add_argument("--offline", action="store_true", help="no API calls: replay saved drafts + rule-based judge")
    r.add_argument("--inject-error", action="store_true", help="plant a false claim to prove the evaluator catches it")
    r.add_argument("--max-retries", type=int, default=2)
    r.add_argument("--memory", default=str(ROOT / "memory" / "memory.json"))
    r.add_argument("--out", default=str(ROOT / "outputs"))
    f = sub.add_parser("feedback")
    f.add_argument("text")
    f.add_argument("--memory", default=str(ROOT / "memory" / "memory.json"))
    m = sub.add_parser("memory")
    m.add_argument("--memory", default=str(ROOT / "memory" / "memory.json"))
    a = ap.parse_args(argv)

    if a.cmd == "feedback":
        Memory(a.memory).add_feedback(a.text)
        print("Saved. It will be shown to the generator on the next run.")
        return
    if a.cmd == "memory":
        print(json.dumps(Memory(a.memory).data, indent=2, ensure_ascii=False))
        return

    facts = (ROOT / "data" / "rag_facts.md").read_text(encoding="utf-8")
    memory = Memory(a.memory)
    distill = None
    if a.offline:
        files = ("draft_v2_fixed.md",) if a.inject_error else ("draft_v1_flawed.md", "draft_v2_fixed.md")
        gen, judge = FixtureGenerator(ROOT / "fixtures", files), HeuristicJudge()
        print("OFFLINE MODE: saved drafts + rule-based judge. Use it for demos and tests only.")
    else:
        from .llm import make_llm
        gen_llm = make_llm("generator")
        judge_llm = make_llm("judge")  # a different model for judging is better, if you have one
        gen, judge, distill = LLMGenerator(gen_llm), LLMJudge(judge_llm), _make_distill(judge_llm)

    res = run_pipeline(a.topic, gen, judge, memory, facts, a.max_retries, a.inject_error, distill)
    out = write_outputs(res, a.out)
    print(f"\nStatus: {res.status}  |  attempts: {len(res.attempts)}  |  files: {out}")


if __name__ == "__main__":
    main()
