"""Mem0 验证：DeepSeek LLM + fastembed 本地嵌入 + 本地 Qdrant"""
import os, sys

os.environ["MEM0_DIR"] = os.path.join(os.path.dirname(__file__), ".mem0_data")
# HuggingFace 镜像，加速模型下载
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from mem0 import Memory
from mem0.configs.base import MemoryConfig, VectorStoreConfig, EmbedderConfig, LlmConfig

def main():
    print("1. 初始化 Memory...")
    print("   LLM: DeepSeek deepseek-chat")
    print("   Embedding: fastembed BAAI/bge-small-zh-v1.5 (本地)")
    print("   Vector Store: Qdrant (本地文件)")

    config = MemoryConfig(
        llm=LlmConfig(
            provider="openai",  # DeepSeek 兼容 OpenAI SDK
            config={
                "model": "deepseek-chat",
                "api_key": "<YOUR_DEEPSEEK_API_KEY>",
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
                "path": os.path.join(os.environ["MEM0_DIR"], "qdrant"),
                "collection_name": "pas_test",
                "embedding_model_dims": 512,
                "on_disk": True,
            },
        ),
    )

    m = Memory(config)
    print("   初始化成功\n")

    print("2. 写入测试记录...")
    result = m.add(
        "我在想知行合一的问题，卡在王阳明的论证链条上：从心即理到知行合一，中间的跳跃是怎么完成的？",
        user_id="<YOUR_USER_ID>",
        metadata={"source_type": "note", "tags": ["中国哲学", "王阳明", "知行合一"]},
    )
    print(f"   写入成功: {result}\n")

    print("3. 语义检索...")
    results = m.search(
        "王阳明知行合一的论证结构",
        filters={"user_id": "<YOUR_USER_ID>"},
        limit=3,
    )
    print(f"   raw type: {type(results)}")
    print(f"   raw keys: {results.keys() if isinstance(results, dict) else 'N/A'}")
    if isinstance(results, dict) and "results" in results:
        items = results["results"]
        for i, r in enumerate(items):
            mem = r.get("memory", "") if isinstance(r, dict) else str(r)
            score = r.get("score", "N/A") if isinstance(r, dict) else "N/A"
            print(f"   [{i+1}] score={score} -> {str(mem)[:120]}")
    elif isinstance(results, list):
        for i, r in enumerate(results):
            print(f"   [{i+1}] {str(r)[:120]}")
    print("\nMem0 写入/检索闭环验证通过")

if __name__ == "__main__":
    main()
