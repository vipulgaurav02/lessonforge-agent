# Introduction to RAG

## 1. What is RAG?

RAG is a technique where an LLM answers questions by first doing a retrieval over an external corpus and then conditioning its generation on the retrieved context, which makes it far more accurate than a vanilla model that relies only on its parametric memory.

## 2. Why do we need RAG?

LLMs hallucinate and their knowledge is frozen at the training cutoff, so enterprises use RAG to ground responses in proprietary data without paying for expensive pre-training runs.

## 3. How does RAG work?

First the documents are converted into embeddings and stored in a vector database. When a user asks something, the query is also embedded, and a similarity search returns the top-k chunks. Then, under the hood, the LLM is retrained on those chunks every time a question is asked, so that the model weights absorb the new knowledge before it produces the answer.

## 4. Summary

RAG is a piece of cake once you understand it. It gives better answers because the model is updated with your data.
