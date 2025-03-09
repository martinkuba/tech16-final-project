---
alias: null
date: 2025-02-11
tags: null
---

https://github.com/langchain-ai/langchain

LangSmith
https://smith.langchain.com/o/a48168d8-83ef-4a80-905d-bca95e43954c/settings

[MapReduceDocumentsChain — 🦜🔗 LangChain documentation](https://python.langchain.com/v0.2/api_reference/langchain/chains/langchain.chains.combine_documents.map_reduce.MapReduceDocumentsChain.html)

[Summarize Text | 🦜️🔗 LangChain](https://python.langchain.com/v0.2/docs/tutorials/summarization/#orchestration-via-langgraph)

Example of chunking
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

text = """This is a long paragraph. It has multiple sentences. 
Splitting it is tricky. RecursiveCharacterTextSplitter handles it more intelligently."""

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=50,    # Maximum size per chunk
    chunk_overlap=10  # Overlap 10 characters for context
)
chunks = text_splitter.split_text(text)
print(chunks)
```