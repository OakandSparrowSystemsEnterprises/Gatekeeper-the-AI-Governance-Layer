import urllib.request
import json

payload = json.dumps({
    "model": "mistralai/mistral-7b-instruct-v0.3",
    "messages": [{"role": "user", "content": "Say hello."}],
    "max_tokens": 50
}).encode()

req = urllib.request.Request(
    "http://localhost:1234/v1/chat/completions",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req, timeout=30) as resp:
    print(json.dumps(json.loads(resp.read()), indent=2))
