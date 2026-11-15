# Fact sheet: Retrieval-Augmented Generation (RAG)

The evaluator judges accuracy ONLY against this sheet. The generator is told to stay inside it.

F1. RAG stands for Retrieval-Augmented Generation. The idea was introduced in 2020 by Lewis et al. (Facebook AI Research with University College London and New York University) in the paper "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks".
F2. A large language model (LLM) learns from a huge amount of text up to a fixed training cutoff date. After that date it does not learn new facts by itself.
F3. An LLM has not seen private documents (a company's files, a college's notices) unless they were in its training text.
F4. An LLM can hallucinate: it can write a wrong answer in a confident voice.
F5. RAG adds a retrieval step BEFORE the model writes its answer: the system finds relevant text from an external knowledge source, adds that text to the model's input, and the model writes its answer using that text.
F6. The usual steps are: (0) prepare once: split documents into chunks, turn each chunk into an embedding (a list of numbers that captures meaning), store them in a vector database or index; (1) retrieve: turn the question into an embedding and find the chunks closest in meaning; (2) augment: put the chosen chunks and the question together into the model's input; (3) generate: the LLM writes the answer using those chunks.
F7. Text with similar meaning gets similar embeddings (the numbers are close to each other).
F8. RAG does NOT retrain, fine-tune or change the model's weights. It changes only what the model reads. To update the knowledge, you update the documents.
F9. Benefits: answers can use fresh and private information; answers can point to their source documents; it usually reduces (but does not remove) hallucinations; updating documents is cheaper and faster than retraining a model.
F10. Limits: if retrieval finds the wrong chunks, the answer can still be wrong; the quality of the documents matters; the extra search step adds some delay.
F11. RAG and fine-tuning are different. Fine-tuning changes the model's weights by more training. RAG leaves the model unchanged.
