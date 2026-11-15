from pathlib import Path

from lessonforge.evaluator import HeuristicJudge, LLMJudge, deterministic_checks, evaluate
from lessonforge.generator import FixtureGenerator, split_changes
from lessonforge.memory import Memory
from lessonforge.pipeline import inject_false_claim, rejection_log_md, run_pipeline
from lessonforge.rubric import CHECKS

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "fixtures"
FACTS = (ROOT / "data" / "rag_facts.md").read_text()
quiet = lambda *_: None


def good():
    return split_changes((FIX / "draft_v2_fixed.md").read_text())[0]


def bad():
    return split_changes((FIX / "draft_v1_flawed.md").read_text())[0]


def run(tmp_path, files, **kw):
    mem = Memory(tmp_path / "m.json")
    gen = FixtureGenerator(FIX, files)
    return run_pipeline("Introduction to RAG", gen, HeuristicJudge(), mem, FACTS, log=quiet, **kw), mem


def test_good_lesson_passes_every_check():
    assert all(r.passed for r in evaluate(good(), HeuristicJudge(), FACTS))


def test_flawed_lesson_fails_many_checks():
    failed = {r.id for r in evaluate(bad(), HeuristicJudge(), FACTS) if not r.passed}
    assert {"ACC2", "JAR1", "LANG1", "LANG2", "STRUCT1", "EX2"} <= failed


def test_every_check_gets_a_hard_verdict():
    res = evaluate(good(), HeuristicJudge(), FACTS)
    assert [r.id for r in res] == [c.id for c in CHECKS]
    assert all(isinstance(r.passed, bool) for r in res)


def test_loop_fixes_flawed_draft_on_retry(tmp_path):
    res, _ = run(tmp_path, ["draft_v1_flawed.md", "draft_v2_fixed.md"])
    assert res.status == "SHIPPED" and len(res.attempts) == 2
    assert not res.attempts[0].passed and res.attempts[1].passed
    assert "What changed on retry" in rejection_log_md(res)


def test_loop_always_terminates_and_escalates(tmp_path):
    res, _ = run(tmp_path, ["draft_v1_flawed.md"], max_retries=2)
    assert res.status == "NEEDS_HUMAN_REVIEW"
    assert len(res.attempts) == 3  # 1 try + 2 retries, never more


def test_zero_retries_means_one_attempt(tmp_path):
    res, _ = run(tmp_path, ["draft_v1_flawed.md"], max_retries=0)
    assert len(res.attempts) == 1


def test_evaluator_catches_deliberate_error():
    bad_lesson = inject_false_claim(good())
    failed = [r for r in evaluate(bad_lesson, HeuristicJudge(), FACTS) if not r.passed]
    assert [r.id for r in failed] == ["ACC2"]
    assert "retrained" in failed[0].evidence


def test_injected_error_is_fixed_by_retry(tmp_path):
    res, _ = run(tmp_path, ["draft_v2_fixed.md"], inject_error=True)
    assert res.status == "SHIPPED" and len(res.attempts) == 2
    assert "retrained on your documents" not in res.lesson


def test_memory_persists_and_feeds_next_run(tmp_path):
    _, mem = run(tmp_path, ["draft_v1_flawed.md", "draft_v2_fixed.md"])
    again = Memory(tmp_path / "m.json")
    assert again.data["fail_counts"]["ACC2"] == 1
    assert any("ACC2" in h for h in again.hints())


def test_repeated_failures_get_promoted(tmp_path):
    for _ in range(3):
        run(tmp_path, ["draft_v1_flawed.md", "draft_v2_fixed.md"])
    mem = Memory(tmp_path / "m.json")
    assert any(h.startswith("MUST") for h in mem.hints())
    assert "ACC2" in mem.judge_notes()


def test_errors_we_plant_are_not_learned(tmp_path):
    _, mem = run(tmp_path, ["draft_v2_fixed.md"], inject_error=True)
    assert "ACC2" not in mem.data["fail_counts"]


def test_human_feedback_reaches_generator_hints(tmp_path):
    mem = Memory(tmp_path / "m.json")
    mem.add_feedback("use more Hindi-speaking examples")
    assert any("Hindi" in h for h in Memory(tmp_path / "m.json").hints())


class BrokenLLM:
    def complete(self, *a, **k):
        return "not json at all"


def test_llm_judge_fails_closed_on_broken_output():
    res = LLMJudge(BrokenLLM()).judge(good(), FACTS)
    assert res and all(not r.passed for r in res.values())
