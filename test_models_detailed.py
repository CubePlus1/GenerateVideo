"""Better test script - check actual response content."""
import httpx
import json

API_ENDPOINT = "http://127.0.0.1:58778/v1/chat/completions"
API_TOKEN = "sk114514"

MODELS_TO_TEST = [
    "veo-3.1",
    "veo-3",
    "veo_3_1",
    "wan2.2-kf2v-flash",
]

def test_model_detailed(model_name):
    """Test model and show actual response."""
    payload = {
        "model": model_name,
        "messages": [{
            "role": "user",
            "content": [{"type": "text", "text": "测试"}]
        }],
        "stream": True
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    print(f"\n{'='*60}")
    print(f"测试模型: {model_name}")
    print('='*60)

    try:
        with httpx.Client(timeout=10) as client:
            with client.stream("POST", API_ENDPOINT, json=payload, headers=headers) as response:
                print(f"状态码: {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")

                # Read first few lines
                print("\n前几行响应:")
                print("-" * 60)

                line_count = 0
                for line in response.iter_lines():
                    if line_count >= 5:  # Only show first 5 lines
                        break
                    decoded = line.decode('utf-8') if isinstance(line, bytes) else line
                    print(decoded)

                    # Check for error
                    if '"error"' in decoded or '不支持' in decoded:
                        print(f"\n⚠️ 发现错误信息!")
                        return False

                    line_count += 1

                print("-" * 60)
                return True

    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

if __name__ == "__main__":
    print("详细测试视频生成模型")
    print(f"API: {API_ENDPOINT}\n")

    for model in MODELS_TO_TEST:
        test_model_detailed(model)

    print("\n" + "="*60)
    print("请查看上面的响应，找到没有错误信息的模型")
    print("="*60)
