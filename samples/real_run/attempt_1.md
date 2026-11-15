# Introduction to RAG (Retrieval-Augmented Generation)

## 1. What is RAG?

RAG stands for Retrieval-Augmented Generation. The idea was introduced in 2020 by Lewis and his team. They worked at Facebook AI Research, University College London, and New York University. They published this method in a research paper called "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks".

Let us break down the name word by word:
- **Retrieval:** This means finding and bringing back relevant information from an outside store of documents.
- **Augmented:** This means adding extra helpful information to the input.
- **Generation:** This means writing an answer using that gathered information.

An everyday example is an open-book exam in college. In a normal closed-book exam, you must answer only from memory. If you forget a fact, you might guess or fail. In an open-book exam, you carry your textbook. First, you search for the right page in your book. Next, you read that page. Finally, you write your answer using that text. 

RAG works just like an open-book exam for a computer.

## 2. Why do we need RAG?

A large language model (LLM) is an AI program trained on a huge amount of text. An LLM is smart, but it has two big problems.

First, an LLM learns facts only up to a fixed training cutoff date. A training cutoff date is the day the model stops learning new text. After that date, the LLM does not learn new facts by itself. Also, the LLM has not seen private documents, such as your college's new circulars.

Second, an LLM can hallucinate. To hallucinate means to write a wrong answer in a very confident voice. When a model does not know a fact, it might make up an incorrect reply.

RAG solves these problems. It finds the newest, correct documents before the model replies. RAG changes only what the model reads, never the model itself. It does not retrain or alter the model.

## 3. How does RAG work?

Before we look at the steps, here are three simple technical terms:
- A **chunk** is a short, cut piece of a larger document.
- An **embedding** is a list of numbers that captures the meaning of a text.
- A **vector database** is a storage system built to hold and search embeddings.

RAG works in four clear steps:

1. **Prepare (done once):**
   First, you split large documents into small chunks. Next, you convert each chunk into an embedding. Texts with similar meanings get numbers that are close to each other. Finally, you store these numbers in a vector database or index.

2. **Retrieve:**
   A user asks a question. The system turns this question into an embedding. Then, it finds the document chunks whose numbers are closest in meaning to the question.

3. **Augment:**
   The system takes the chosen chunks and the user's question. It joins them together into one single input for the model.

4. **Generate:**
   The LLM reads this combined text. It writes a clear answer using the exact facts from those chunks.

Fine-tuning is a different method that changes a model's internal weights through more training. RAG is different. RAG leaves the model unchanged. You only change the documents it reads.

## 4. A worked example

Imagine a student asks: "What is the last date to submit the college scholarship form?"

### Without RAG:
The LLM searches only its past memory from training. It has never seen this college's private notice board. It hallucinates and replies confidently: "The last date is 15th August." This answer is completely wrong.

### With RAG:
1. **Prepare:** The college takes its new scholarship notice and saves its text as chunks in a vector database.
2. **Retrieve:** The student asks the question. The system searches the database and finds the notice chunk about scholarship dates.
3. **Augment:** The system gives the model both the notice chunk and the student's question.
4. **Generate:** The LLM reads the notice chunk. It writes: "According to the college notice, the last date is 30th November." 

The answer is now correct. It can even show the exact notice it used.

## 5. Quick recap

- RAG stands for Retrieval-Augmented Generation.
- It finds relevant text from outside documents before the model answers.
- RAG changes what the model reads, never the model itself.
- It allows AI to use fresh facts and private files.
- It reduces hallucinations, but it does not remove them completely.
- Updating documents in RAG is much faster and cheaper than retraining an LLM.
- If the system retrieves the wrong chunks, the final answer can still be wrong.

## Check yourself

1. What does the word "Augmented" mean in RAG?
2. Does RAG change the weights of the AI model?
3. What can happen to the final answer if the retrieval step picks the wrong text chunk?

## Words to know

- **Large language model (LLM):** An AI computer program trained on massive amounts of text to understand and generate language.
- **Hallucinate:** When an AI creates a false or incorrect statement with strong confidence.
- **Chunk:** A small piece cut out from a larger text document.
- **Embedding:** A list of numbers that represents the meaning of a piece of text.
- **Vector database:** A digital storage tool designed to store and search embeddings quickly.
- **Fine-tuning:** A training process that changes an AI model's internal weights with new data.
