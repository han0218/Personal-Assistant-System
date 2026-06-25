"""
PAS Mem0 配置文件
=================
LLM: DeepSeek (OpenAI 兼容接口)
Embedding: fastembed (本地免费)
Vector Store: Qdrant (本地文件存储)

使用方式:
    from mem0_config import get_memory
    m = get_memory()
    m.add("...", user_id="<YOUR_USER_ID>")
    m.search("...", filters={"user_id": "<YOUR_USER_ID>"})

环境变量:
    DEEPSEEK_API_KEY  — DeepSeek API Key（必须）
    MEM0_DATA_DIR     — Mem0 数据目录（可选，默认库根 .mem0_data/）
"""

import atexit
import os

from mem0 import Memory
from qdrant_client import QdrantClient
from mem0.configs.base import (
    MemoryConfig,
    VectorStoreConfig,
    EmbedderConfig,
    LlmConfig,
)

# ---- 路径 ----
PAS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEM0_DATA_DIR = os.environ.get("MEM0_DATA_DIR", os.path.join(PAS_ROOT, ".mem0_data"))
QDRANT_PATH = os.path.join(MEM0_DATA_DIR, "qdrant")

# ---- 模型下载镜像 ----
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

# ---- API Key ----
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise RuntimeError("请设置环境变量 DEEPSEEK_API_KEY")

_qdrant_client: QdrantClient | None = None
_memory_instance: Memory | None = None
_knowledge_instance: Memory | None = None


def _get_qdrant_client() -> QdrantClient:
    """返回共享的本地 Qdrant 客户端，避免同目录多实例独占锁冲突。"""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(path=QDRANT_PATH)
    return _qdrant_client


def _close_qdrant_client() -> None:
    if _qdrant_client is not None:
        _qdrant_client.close()


atexit.register(_close_qdrant_client)


def _build_config(collection_name: str) -> MemoryConfig:
    return MemoryConfig(
        llm=LlmConfig(
            provider="openai",
            config={
                "model": "deepseek-chat",
                "api_key": DEEPSEEK_API_KEY,
                "openai_base_url": "https://api.deepseek.com/v1",
            },
        ),
        embedder=EmbedderConfig(
            provider="fastembed",
            config={
                "model": "BAAI/bge-small-zh-v1.5",
                "embedding_dims": 512,
            },
        ),
        vector_store=VectorStoreConfig(
            provider="qdrant",
            config={
                "path": QDRANT_PATH,
                "client": _get_qdrant_client(),
                "collection_name": collection_name,
                "embedding_model_dims": 512,
                "on_disk": True,
            },
        ),
    )


def get_config() -> MemoryConfig:
    """返回 pool 层的 Mem0 配置。"""
    return _build_config("pas_pool")


def get_memory() -> Memory:
    """返回 pool 层 Mem0 Memory 单例。"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = Memory(get_config())
    return _memory_instance


def get_knowledge_config() -> MemoryConfig:
    """返回知识层的 Mem0 配置（独立 collection: pas_knowledge）。"""
    return _build_config("pas_knowledge")


def get_knowledge_memory() -> Memory:
    """返回知识层 Mem0 Memory 单例。"""
    global _knowledge_instance
    if _knowledge_instance is None:
        _knowledge_instance = Memory(get_knowledge_config())
    return _knowledge_instance