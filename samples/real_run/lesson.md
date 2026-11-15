# Introduction to RAG (Retrieval-Augmented Generation)

## 1. What is RAG?

RAG stands for Retrieval-Augmented Generation. Lewis and his team introduced this idea in 2020. They worked at Facebook AI Research, University College London, and New York University. They shared this method in a paper called "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks".

Let us break down the name word by word:
- **Retrieval:** This means finding and bringing back relevant text from an outside source.
- **Augmented:** This means adding extra helpful information to an input.
- **Generation:** This means writing an answer using that gathered information.

Think about an open-book exam in a college. In a closed-book exam, you must answer only from memory. If you forget a fact, you might guess or fail. In an open-book exam, you carry your textbook with you. First, you search for the right chapter in your book. Next, you read the page carefully. Finally, you write your answer using the text from that page. 

RAG works just like an open-book exam for a computer program.

## 2. Why do we need RAG?

A large language model (LLM) is an AI program trained on a huge amount of text. An LLM is powerful, but it has two major problems.

First, an LLM learns facts only up to a fixed training cutoff date. A training cutoff date is the day when the model stops learning new text. After that date, the model does not learn new facts by itself. Also, an LLM has not seen private documents, such as your college's notices.

Second, an LLM can hallucinate. To hallucinate means to write a wrong answer in a confident voice. When a model does not know an answer, it might still write an incorrect reply.

RAG solves these two problems. It finds relevant text from outside documents before the model replies. RAG changes only what the model reads, never the model itself.

## 3. How does RAG work?

Before we look at the steps, let us understand a few technical terms:
- A **chunk** is a small piece of text cut from a larger document.
- An **embedding** is a list of numbers that captures the meaning of a text.
- A **vector database** is a storage system built to hold and search embeddings.
- Model **weights** are the internal settings inside an AI model that control how it responds.
- **Fine-tuning** is a method that changes a model's weights through extra training.

RAG works in four clear steps:

1. **Prepare (done once):**
   First, you split your documents into small chunks. Next, you turn each chunk into an embedding. Text with similar meaning gets similar embeddings with numbers close together. Finally, you store these numbers in a vector database or index.

2. **Retrieve:**
   A user asks a question. The system turns this question into an embedding. Then, it finds the chunks that are closest in meaning to the question.

3. **Augment:**
   The system puts the chosen chunks and the question together into the model's input.

4. **Generate:**
   The LLM reads this combined text. It writes an answer using facts from those chunks.

RAG does not retrain, fine-tune, or change the model's weights. Fine-tuning changes the model's weights by more training. In contrast, RAG leaves the model unchanged. To update the knowledge in RAG, you only need to update the documents.

## 4. A worked example

Imagine a student asks: "What is the last date to submit the college scholarship form?"

### Without RAG:
The LLM searches only its past memory from training. It has never seen this college's private notice board. The model hallucinates and replies: "The last date is 15th August." This answer sounds confident, but it is completely wrong.

### With RAG:
1. **Prepare:** The college takes its new scholarship circular. It splits the circular into chunks and saves their embeddings in a vector database.
2. **Retrieve:** The student asks the question. The system searches the vector database and finds the chunk about scholarship dates.
3. **Augment:** The system joins the notice chunk and the student's question into one input.
4. **Generate:** The LLM reads the notice chunk. It writes: "According to the college notice, the last date is 30th November."

The answer is now correct. It can even point to the exact college notice it used.

## 5. Quick recap

- RAG stands for Retrieval-Augmented Generation.
- It finds relevant text from an outside source before the model writes an answer.
- RAG changes what the model reads, never the model itself.
- It allows an AI to use fresh facts and private documents.
- It usually reduces hallucinations, but it does not remove them completely.
- Updating documents is cheaper and faster than retraining a model.
- If the retrieval step finds the wrong chunks, the answer can still be wrong.

## Check yourself

1. What does the word "Augmented" mean in RAG?
2. Does RAG change the internal weights of an AI model?
3. What can happen to the final answer if the retrieval step picks the wrong text chunk?

## Words to know

- **Large language model (LLM):** An AI program trained on a huge amount of text.
- **Hallucinate:** To write a wrong answer in a confident voice.
- **Chunk:** A small piece of text cut from a larger document.
- **Embedding:** A list of numbers that captures the meaning of a text.
- **Vector database:** A storage system built to hold and search embeddings.
- **Weights:** The internal settings inside an AI model that control how it responds.
- **Fine-tuning:** A method that changes a model's weights through extra training.
