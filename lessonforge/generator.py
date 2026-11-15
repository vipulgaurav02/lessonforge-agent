"""Generators: write the lesson. On a retry they receive the failed draft + the exact failure reasons."""
from pathlib import Path

CHANGES_MARK = "---CHANGES---"


def split_changes(text):
    """Split model output into (lesson, changes_note)."""
    if CHANGES_MARK in text:
        lesson, changes = text.split(CHANGES_MARK, 1)
        return lesson.strip() + "\n", changes.strip()
    return text.strip() + "\n", ""


SYSTEM = """You are an expert teacher who writes beginner lessons for Indian learners.
LEARNER: 12th-grade graduate, non-English-medium school, limited English vocabulary, knows nothing about AI, wants to start an AI career.

WRITING RULES
- Short sentences. Aim for 10-14 words each. Never more than 25.
- Everyday English. No idioms or slang.
- Explain every technical term in one plain sentence the first time you use it. Never use a term before explaining it.
- Use Indian everyday context where natural (exams, college, notices, trains).
- Use ONLY facts from the FACT SHEET. Do not invent facts, numbers or names.

REQUIRED STRUCTURE (Markdown, 500-1000 words total)
# Introduction to RAG (Retrieval-Augmented Generation)
## 1. What is RAG?        (explain the full name word by word, plus one everyday analogy)
## 2. Why do we need RAG? (at least two real problems it helps with)
## 3. How does RAG work?  (ordered steps: prepare, retrieve, augment, generate)
## 4. A worked example    (one question, answered without RAG, then with RAG, step by step)
## 5. Quick recap         (short bullet list)
## Check yourself         (exactly 3 numbered questions)
## Words to know          (short glossary)

OUTPUT: the lesson in Markdown only. If you are fixing a failed draft, after the lesson print a line
---CHANGES---
then one bullet per failed check saying what you changed."""


class LLMGenerator:
    def __init__(self, llm):
        self.llm = llm

    def generate(self, topic, attempt, previous, failures, hints, facts):
        parts = [f"TOPIC: {topic}", f"FACT SHEET:\n{facts}"]
        if hints:
            parts.append("RULES LEARNED FROM EARLIER RUNS (follow them):\n" + "\n".join(f"- {h}" for h in hints))
        if previous:
            fl = "\n".join(f"- {r.id}: {r.reason}" + (f' (evidence: "{r.evidence}")' if r.evidence else "")
                           for r in failures)
            parts.append("YOUR PREVIOUS DRAFT FAILED REVIEW.\nFAILED CHECKS:\n" + fl +
                         f"\n\nPREVIOUS DRAFT:\n{previous}\n\nRewrite the whole lesson so every failed check passes "
                         "and nothing that already passed breaks. Then add the ---CHANGES--- section.")
        else:
            parts.append("Write the lesson now.")
        return split_changes(self.llm.complete(SYSTEM, "\n\n".join(parts), temperature=0.7, max_tokens=4000))


class FixtureGenerator:
    """Offline generator: replays saved drafts (first a flawed one, then a fixed one). For demos and tests."""

    def __init__(self, fixtures_dir, files=("draft_v1_flawed.md", "draft_v2_fixed.md")):
        self.dir, self.files = Path(fixtures_dir), list(files)

    def generate(self, topic, attempt, previous, failures, hints, facts):
        name = self.files[min(attempt, len(self.files) - 1)]
        return split_changes((self.dir / name).read_text(encoding="utf-8"))
