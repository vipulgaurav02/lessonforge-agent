"""The rubric: hard pass/fail checkpoints. No partial credit.

kind="code" -> measured by Python (cheap, deterministic, cannot be argued with)
kind="llm"  -> needs reading comprehension, so a separate LLM judge decides
`hint` is the default rule shown to the generator after this check has failed.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Check:
    id: str
    dimension: str
    question: str
    kind: str
    hint: str


CHECKS = [
    Check("ACC1", "accurate & grounded",
          "Every factual claim agrees with the fact sheet. Nothing is invented. Nothing says RAG is perfect or never wrong.",
          "llm", "Only state facts from the fact sheet. Never say RAG removes every mistake."),
    Check("ACC2", "accurate & grounded",
          "The lesson never says or implies that RAG retrains, fine-tunes or otherwise changes the model itself.",
          "llm", "Say clearly that RAG changes what the model reads, never the model itself."),
    Check("LANG1", "beginner-friendly language",
          "Average sentence length is 15 words or fewer.",
          "code", "Use short sentences. Aim for 10 to 14 words each."),
    Check("LANG2", "beginner-friendly language",
          "No sentence is longer than 25 words.",
          "code", "Split any sentence that is longer than 25 words."),
    Check("LANG3", "beginner-friendly language",
          "Uses everyday English. No idioms, slang or phrasal expressions that a non-native 12th-grade reader may not know.",
          "llm", "Avoid idioms and slang (for example 'piece of cake', 'under the hood'). Use plain words."),
    Check("JAR1", "clear, no unexplained jargon",
          "Every technical term is explained in plain words the first time it appears, before it is used again.",
          "llm", "Explain each technical term in one plain sentence the first time it appears."),
    Check("EX1", "teaches by example",
          "Uses one everyday analogy (not about computers) that maps clearly onto how RAG works.",
          "llm", "Add one everyday analogy, such as an open-book exam, and map it to RAG."),
    Check("EX2", "teaches by example",
          "Has a worked example with a real question, showing the answer without RAG and with RAG, step by step.",
          "llm", "Add a worked example: one question, answered without RAG and then with RAG."),
    Check("COV1", "covers the key points",
          "Explains WHAT RAG is, including what the name Retrieval-Augmented Generation means.",
          "llm", "Explain the full name word by word."),
    Check("COV2", "covers the key points",
          "Explains WHY it matters: at least two real problems it helps with (old knowledge, private data, hallucination).",
          "llm", "Name at least two problems that RAG helps with."),
    Check("COV3", "covers the key points",
          "Explains HOW it works as ordered steps: prepare, retrieve, augment, generate.",
          "llm", "Show the steps in order: prepare, retrieve, augment, generate."),
    Check("FLOW1", "coherent teaching flow",
          "Sections run What, Why, How, Example, Recap. Each section only uses ideas already explained above it.",
          "llm", "Keep the order What, Why, How, Example, Recap. Do not use a term before it is explained."),
    Check("STRUCT1", "coherent teaching flow",
          "Has 500 to 1000 words, the five required headings in order, and a 'Check yourself' section with 3 numbered questions.",
          "code", "Keep to 500-1000 words with the five headings and 3 'Check yourself' questions."),
]

CHECK_IDS = [c.id for c in CHECKS]
BY_ID = {c.id: c for c in CHECKS}
