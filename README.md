# lessonforge: a self-evaluating lesson generator

Generates a beginner lesson, **judges its own work against hard pass/fail checks**, and regenerates until the lesson clears the bar. If it cannot clear the bar, it **stops and asks a human** instead of shipping a bad lesson.

Topic for the assessment: **Introduction to RAG**.
Learner: a 12th-grade graduate from India, limited English, no AI background.

---

## 1. Quick start

```bash
pip install -r requirements.txt

# Option A: FREE. Get a key at aistudio.google.com (Get API key), then:
export GEMINI_API_KEY=...                  # Windows PowerShell: $env:GEMINI_API_KEY="..."
# Option B: paid Anthropic key
export ANTHROPIC_API_KEY=...

python -m lessonforge run --topic "Introduction to RAG"                  # real run
python -m lessonforge run --topic "Introduction to RAG" --inject-error   # plant a false claim, watch the evaluator catch it
python -m lessonforge feedback "Use one more Indian everyday example"    # teach it from a human note
python -m lessonforge memory                                             # see what it has learned
pytest -q                                                                # 13 tests, no API key needed
```

Free-tier note: Gemini's free tier has a low requests-per-minute limit. If a call is rate-limited, the tool waits and retries by itself, so a run can take a few minutes. Gemini defaults to `gemini-3.8-flash`; pick another model your key can use with `LESSONFORGE_GENERATOR_MODEL` and `LESSONFORGE_JUDGE_MODEL`.

No API key? `--offline` replays saved drafts through the real loop with a rule-based judge. It is for demos and tests only. The lesson for submission must come from a real run.

Each run writes `outputs/run_<time>/`:
`lesson.md` (the passing lesson), `rejection_log.md` (what failed, why, what changed), `run_log.json` (every verdict), `attempt_N.md` (every draft).

## 2. Architecture

```
            topic + fact sheet + learned rules (memory)
                              |
                              v
   .---------------->  GENERATE (LLM)  ---> draft
   |                                          |
   | failed checks + reasons                  v
   | + previous draft               EVALUATE  (13 hard checks)
   |                                 |  code checks  : length, structure (Python)
   |                                 |  LLM judge    : accuracy, jargon, examples, flow
   |                                 v
   |                         all 13 pass?
   |                       yes /        \ no
   |                        v             v
   |                      SHIP      retries left?  (max 2)
   |                                 yes /     \ no
   '---------------------------------'         v
                                       ESCALATE: best draft + log to a human
                              |
                              v
                  MEMORY: record failures, update rules, store feedback
```

| File | Job |
|---|---|
| `rubric.py` | The 13 checks. One place to edit the bar. |
| `generator.py` | Writes the lesson. On retry it gets the old draft plus exact failure reasons. |
| `evaluator.py` | Code checks + LLM judge (+ offline heuristic judge). |
| `pipeline.py` | The loop, the retry cap, escalation, the rejection log. |
| `memory.py` | Persistent learning across runs. |
| `llm.py` | Small model wrappers (Gemini, Anthropic). Add your own provider here. |
| `data/rag_facts.md` | The fact sheet: ground truth for accuracy. |

## 3. The rubric (hard pass/fail, no partial credit)

| Dimension | Checks | How it is judged |
|---|---|---|
| Accurate & grounded | ACC1 claims match the fact sheet, no overclaiming. ACC2 never says RAG retrains the model. | LLM judge |
| Beginner-friendly language | LANG1 average sentence ≤ 15 words. LANG2 no sentence > 25. LANG3 no idioms or slang. | LANG1, LANG2 in Python. LANG3 LLM |
| No unexplained jargon | JAR1 every technical term explained at first use. | LLM judge |
| Teaches by example | EX1 everyday analogy. EX2 worked question with and without RAG. | LLM judge |
| Covers key points | COV1 what, COV2 why (≥ 2 problems), COV3 how (ordered steps). | LLM judge |
| Teaching flow | FLOW1 order and no forward references. STRUCT1 500-1000 words, 5 headings in order, 3 check questions. | FLOW1 LLM. STRUCT1 Python |

## 4. Design decisions and trade-offs

**Why hard pass/fail?** The system must make a ship / don't-ship decision on its own. A score such as 7.5/10 forces a threshold and hides which fact was wrong. A boolean with a reason is also the most useful feedback for the next attempt.

**Why split the rubric between code and an LLM?** Anything measurable (sentence length, word count, headings) is checked by Python. It is free, repeatable and cannot be talked out of a failure. An LLM is used only where meaning must be judged. Fewer LLM checks means fewer places for judge error.

**Why a separate judge call (and ideally a different model)?** A model grades its own writing too kindly. The judge never sees the generator's reasoning. It only sees the lesson, the fact sheet and the checks. `LESSONFORGE_JUDGE_MODEL` lets you use a different model.

**How accuracy is "grounded".** The generator is told to use only `data/rag_facts.md`. The judge checks claims against the same sheet. This gives a fixed reference, so a confident wrong claim cannot pass just because it sounds right. Limit: the lesson is only as accurate as the sheet.

**Judge reliability.** The judge must quote evidence, is told "if unsure, FAIL", runs at temperature 0, and **fails closed**: if its JSON is missing or broken, the check counts as failed, never as passed (`test_llm_judge_fails_closed_on_broken_output`).

**Retry design.** The generator receives its previous draft, the failed checks, and the judge's reasons and evidence, and must report what it changed. Retries are capped at 2, so the loop always ends (`test_loop_always_terminates_and_escalates`).

**Escalation instead of silent shipping.** After the last retry, a failing draft is marked `NEEDS_HUMAN_REVIEW`. The best draft (fewest failures) and the full log go to a person. The promise is "nothing reaches a human unless it cleared the bar, or it is flagged".

**Memory and self-evolution.** After every run, memory stores per-check failure counts, recent failure reasons, one short rule per failing check, and human feedback. Next run, the generator sees these rules. If a check fails 3 or more times, it is **promoted**:
- its rule is shown to the generator as MUST;
- its recent failure reasons are given to the judge as "known failure patterns to look for", which sharpens the rubric where it matters.

In real mode, once a check has failed twice, the rule is distilled by an LLM from the failure reasons. Offline it falls back to the rule written in `rubric.py`. Errors we plant ourselves with `--inject-error` are **not** learned from, so memory is not polluted.

**Why plain Python, not LangGraph or n8n?** The loop has one cycle and three outcomes. Plain Python keeps every decision readable in one short file, with no framework to explain. The diagram above maps one-to-one to a LangGraph graph (generate, evaluate and ship nodes, and a conditional edge for retry or escalate) if the team prefers that.

## 5. Known limits and next steps

- **One LLM judge can still be wrong.** Mitigations: evidence quotes, fail-closed, separate model. Next: run the judge twice and require agreement, and track judge-vs-human agreement.
- **Sentence-length checks are a proxy for readability.** Next: add a word-frequency check against a list of common English words.
- **The fact sheet is hand-written and small.** Next: ground against retrieved source documents, which is RAG applied to its own evaluator.
- **Rules in memory can pile up.** Capped at 8 hints; next: merge similar rules and expire stale ones.
- **No human-in-the-loop UI.** Escalation writes files. Next: a review queue.
- **Learner testing is missing.** Next: test the lesson on real learners and feed their questions back as `feedback`.
