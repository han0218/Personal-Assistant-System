"""Mem0 验证：DeepSeek LLM + fastembed 本地嵌入 + 本地 Qdrant。

公开版测试脚本只验证安装后的基础闭环：写入一条临时记录、检索它、再按 ID 删除。
API Key 从环境变量 DEEPSEEK_API_KEY 读取，不写入仓库文件。
"""

import os
import sys
import uuid
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PAS_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PAS_ROOT / ".pas"))

from mem0 import Memory  # noqa: E402
from mem0_config import get_config  # noqa: E402


TEST_COLLECTION = "pas_test"
TEST_USER_ID = "pas_test_runner"


def _extract_added_ids(result):
    if isinstance(result, dict):
        if result.get("id"):
            return [result["id"]]
        results = result.get("results") or []
        return [item.get("id") for item in results if isinstance(item, dict) and item.get("id")]
    if isinstance(result, list):
        return [item.get("id") for item in result if isinstance(item, dict) and item.get("id")]
    return []


def main():
    if not os.environ.get("DEEPSEEK_API_KEY"):
        raise RuntimeError("请先设置环境变量 DEEPSEEK_API_KEY")

    print("1. 初始化 Memory...")
    config = get_config()
    vector_config = config.vector_store.config
    if isinstance(vector_config, dict):
        vector_config["collection_name"] = TEST_COLLECTION
    else:
        vector_config.collection_name = TEST_COLLECTION
    m = Memory(config)
    print(f"   collection: {TEST_COLLECTION}")

    token = f"pas-public-test-{uuid.uuid4()}"
    added_ids = []

    try:
        print("2. 写入临时测试记录...")
        result = m.add(
            f"这是一条 PAS 公开版安装验证记录，唯一标识：{token}",
            user_id=TEST_USER_ID,
            metadata={"source_type": "test", "token": token},
            infer=False,
        )
        added_ids = _extract_added_ids(result)
        if not added_ids:
            raise RuntimeError(f"写入成功但未拿到记录 ID: {result}")
        print(f"   写入 ID: {added_ids}")

        print("3. 语义检索...")
        response = m.search(
            token,
            filters={"user_id": TEST_USER_ID},
            top_k=3,
        )
        items = response.get("results", []) if isinstance(response, dict) else response
        memories = [item.get("memory", "") for item in items if isinstance(item, dict)]
        if not any(token in memory for memory in memories):
            raise RuntimeError(f"未检索到刚写入的测试记录: {response}")
        print("   检索成功")

    finally:
        for memory_id in added_ids:
            try:
                m.delete(memory_id=memory_id)
                print(f"   已清理测试记录: {memory_id}")
            except Exception as exc:  # pragma: no cover - 清理失败时显式告警
                print(f"   清理失败，请手动检查 {memory_id}: {exc}")

    print("\nMem0 写入/检索/清理闭环验证通过")


if __name__ == "__main__":
    main()
