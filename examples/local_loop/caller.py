import urllib.request
import json

payload = json.dumps({
    "query": "chronic pain topical heavy"
}).encode()

req = urllib.request.Request(
    "http://localhost:8787/recommend",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)

print("[caller] sending request to Gatekeeper...")

with urllib.request.urlopen(req) as resp:
    body = json.loads(resp.read())
    print(f"[caller] response received: {json.dumps(body, indent=2)}")

print("[caller] done — check artifacts/gatekeeper.ndjson")