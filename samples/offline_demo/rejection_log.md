# Rejection log: Introduction to RAG

Final status: **SHIPPED** after 2 attempt(s).

## Attempt 1: REJECTED (11 of 13 checks failed)

| Check | Why it failed | Evidence |
|---|---|---|
| ACC2 | Says or implies the model is retrained/updated, which contradicts fact F8. | Then, under the hood, the LLM is retrained on those chunks every |
| LANG1 | Average sentence length is 22.1 words (limit 15). | - |
| LANG2 | Longest sentence has 44 words (limit 25). | RAG is a technique where an LLM answers questions by first doing |
| LANG3 | Uses the idiom 'piece of cake'. | piece of cake |
| JAR1 | Used without explanation: embedding, vector database. | embedding, vector database |
| EX1 | No everyday analogy found. | - |
| EX2 | No worked example with and without RAG. | - |
| COV1 | Does not explain what RAG is or its full name. | - |
| COV3 | Retrieve/augment/generate steps missing or out of order. | - |
| FLOW1 | Headings out of order or a technical term is used before the How section. | - |
| STRUCT1 | word count is 175 (needs 500-1000); the five headings What/Why/How/Example/Recap are missing or out of order; 'Check yourself' has 0 numbered questions (needs exactly 3). | - |

**What changed on retry (attempt 2):** +67 / -6 lines.

- ACC2: Removed the claim that the LLM is retrained on the chunks. Added clear lines that the LLM is never retrained and that only the documents change.
- JAR1: Explained chatbot, LLM, chunk, embedding, vector database and hallucination at first use. Removed corpus, parametric memory, top-k and similarity search.
- LANG1/LANG2: Split the 40-word sentences into short ones of about 10-14 words.
- LANG3: Removed the idioms "under the hood" and "a piece of cake".
- EX1/EX2: Added the open-book exam analogy and a worked example with and without RAG.
- COV1/COV2/COV3: Explained the full name word by word, added three problems, and listed the steps in order.
- FLOW1/STRUCT1: Added the five headings in order, a recap, three "Check yourself" questions and a glossary.

## Attempt 2: PASSED all checks
