
from langchain_ollama import ChatOllama
import os
import asyncio

ANALYST_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_CONCURRENCY_LIMIT = os.getenv("OLLAMA_CONCURRENCY_LIMIT", 5)


ollama_semaphore = asyncio.Semaphore(int(OLLAMA_CONCURRENCY_LIMIT))

llm = ChatOllama(model=ANALYST_MODEL, temperature=0.1, num_ctx=8192)
