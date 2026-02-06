"""Test script to find the correct video generation model name."""
import httpx
import json

API_ENDPOINT = "http://127.0.0.1:58778/v1/chat/completions"
API_TOKEN = "sk114514"

# Common model names to test
MODELS_TO_TEST = [
    "veo-3.1",
    "veo-3",
    "veo_3_1",
    "veo3.1",
    "wan2.2-kf2v-flash",
    "wanx2.1-kf2v-plus",
    "video-generator",
    "i2v",
    "image-to-video",
]

def test_model(model_name):
    """Test if a model name is supported."""
    payload = {
        "model": model_name,
        "messages": [{
            "role": "user",
            "content": [{"type": "text", "text": "test"}]
        }],
        "stream": True
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        with httpx.Client(timeout=10) as client:
            with client.stream("POST", API_ENDPOINT, json=payload, headers=headers) as response:
                response.read()
                if response.status_code == 200:
                    return "✅ 支持"
                elif response.status_code == 401:
                    return "🔑 认证错误"
                else:
                    # Check error message
                    try:
                        error_data = json.loads(response.text)
                        if "不支持的模型" in str(error_data) or "unsupported model" in str(error_data).lower():
                            return "❌ 不支持"
                        else:
                            return f"⚠️ 其他错误: {response.status_code}"
                    except:
                        return f"⚠️ HTTP {response.status_code}"
    except Exception as e:
        return f"❌ 错误: {str(e)[:50]}"

if __name__ == "__main__":
    print("=" * 60)
    print("测试视频生成模型")
    print(f"API 地址: {API_ENDPOINT}")
    print("=" * 60)
    print()

    for model in MODELS_TO_TEST:
        result = test_model(model)
        print(f"{model:30} {result}")

    print()
    print("=" * 60)
    print("提示: 找到标记为 ✅ 的模型名称，更新到 src/config.py 中")
    print("=" * 60)
