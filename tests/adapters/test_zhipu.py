from src.adapters.zhipu import ZhipuAdapter


def test_supports_zhipu_models():
    adapter = ZhipuAdapter(
        name="zhipu",
        api_key="test-key",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        models=["glm-4", "glm-4-plus", "glm-4-flash"],
    )
    assert adapter.supports_model("glm-4")
    assert adapter.supports_model("glm-4-plus")
    assert adapter.supports_model("glm-4-flash")
    assert not adapter.supports_model("gpt-4o")
