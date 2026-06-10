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

import os
import sys

from mem0 import Memory
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


def get_config() -> MemoryConfig:
    """返回 PAS 的 Mem0 配置"""
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
                "collection_name": "pas_pool",
                "embedding_model_dims": 512,
                "on_disk": True,
            },
        ),
    )


# 全局单例，避免重复加载模型
_memory_instance: Memory | None = None


def get_memory() -> Memory:
    """返回 Mem0 Memory 单例"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = Memory(get_config())
    return _memory_instance
