# Introduction to RAG (Retrieval-Augmented Generation)

## 1. What is RAG?

RAG is a way to help an AI chatbot give better answers. A chatbot is a program you can chat with, like ChatGPT. The full name of RAG is Retrieval-Augmented Generation. Do not worry about the long name. Let us break it into three small words.

- **Retrieval** means finding. The AI finds useful information.
- **Augmented** means added to. The information is added to your question.
- **Generation** means writing. The AI writes the final answer.

Chatbots like ChatGPT and Claude are built on a large language model, or LLM. An LLM is a program that learned to read and write by studying a huge amount of text. Without RAG, it answers only from what it learned in the past.

Think about two kinds of exams. In a closed-book exam, you can only use your memory. In an open-book exam, you can look at your book first. Then you write the answer. RAG turns the chatbot's closed-book exam into an open-book exam.

## 2. Why do we need RAG?

An LLM is smart, but it has three problems.

1. **Old knowledge.** An LLM stops learning on a fixed date. It does not know news or rules that came after that date.
2. **No private knowledge.** An LLM has not read your college notices, your company files, or your notes.
3. **Confident mistakes.** Sometimes an LLM gives a wrong answer in a very sure voice. This is called a hallucination.

RAG helps with all three problems. The AI can read fresh and private documents before it answers. When the answer comes from a real document, mistakes become less common. The AI can also show which document it used. RAG does not remove every mistake, but it reduces them.

Some people ask, "Why not teach the AI again with the new documents?" That is slow and costly. With RAG, you only change the documents. The AI itself does not change.

## 3. How does RAG work?

RAG has one preparation step and three main steps.

**Step 0: Prepare the library (done once).** First, we collect our documents. We cut each document into small pieces called chunks. Then a special program changes every chunk into a list of numbers called an embedding. These numbers capture the meaning of the text. Chunks with similar meaning get similar numbers. We save all embeddings in a vector database. A vector database is a store that can quickly find similar lists of numbers.

**Step 1: Retrieve.** The user asks a question. The same program changes the question into numbers. The system searches the vector database. It picks the few chunks closest in meaning to the question.

**Step 2: Augment.** The system builds a new message for the LLM. It puts the chosen chunks and the user's question together. For example: "Use only these notes to answer. Notes: the chunks. Question: the user's question."

**Step 3: Generate.** The LLM reads the notes and the question. Then it writes the answer using the notes.

Remember: the LLM is not retrained at any step. It simply gets better material to read.

## 4. A worked example

Imagine a college in Bengaluru has an exam-help chatbot. A student asks:

**Question:** "What is the last date to pay the exam fee?"

**Without RAG:** The chatbot has never seen this year's notice. It may guess an old date from the past. The student could get a wrong answer.

**With RAG:**

1. Retrieve: The system searches the college notices. It finds this chunk: "Exam fee last date: 15 December."
2. Augment: The system gives this chunk and the question to the LLM.
3. Generate: The LLM answers, "The last date to pay the exam fee is 15 December." It can also say which notice it used.

Next year, the college uploads a new notice. The chatbot then gives the new date at once. Nobody has to retrain anything.

## 5. Quick recap

- RAG means Retrieval (find), Augmented (add), Generation (write).
- It makes a chatbot answer like an open-book exam.
- It helps with old knowledge, missing private knowledge, and many confident mistakes.
- The steps are: prepare the documents, retrieve, augment, generate.
- RAG changes the information the AI reads. It does not change the AI itself.
- RAG can still fail if it finds the wrong chunks, so good documents matter.

## Check yourself

1. What do the three words in Retrieval-Augmented Generation mean?
2. Which two problems of an LLM can RAG help to solve?
3. In the college example, which step finds the exam notice?

## Words to know

- **LLM:** a program that reads and writes text after learning from a huge amount of text.
- **Chunk:** a small piece of a document.
- **Embedding:** a list of numbers that captures the meaning of a text.
- **Vector database:** a store that finds similar embeddings quickly.
- **Hallucination:** a confident but wrong answer from an AI.

---CHANGES---
- ACC2: Removed the claim that the LLM is retrained on the chunks. Added clear lines that the LLM is never retrained and that only the documents change.
- JAR1: Explained chatbot, LLM, chunk, embedding, vector database and hallucination at first use. Removed corpus, parametric memory, top-k and similarity search.
- LANG1/LANG2: Split the 40-word sentences into short ones of about 10-14 words.
- LANG3: Removed the idioms "under the hood" and "a piece of cake".
- EX1/EX2: Added the open-book exam analogy and a worked example with and without RAG.
- COV1/COV2/COV3: Explained the full name word by word, added three problems, and listed the steps in order.
- FLOW1/STRUCT1: Added the five headings in order, a recap, three "Check yourself" questions and a glossary.
