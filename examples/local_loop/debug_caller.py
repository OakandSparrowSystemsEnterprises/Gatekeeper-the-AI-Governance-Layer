import urllib.request
import json

payload = json.dumps({"query": "A runaway trolley is heading toward five people tied to the tracks. You can pull a lever to divert it to a side track where one person is tied. Do you pull the lever? Reason through this carefully."}).encode()

req = urllib.request.Request("http://localhost:8787/recommend", data=payload, headers={"Content-Type": "application/json"}, method="POST")

print("[caller] sending trolley problem through Gatekeeper... please wait up to 60 seconds")

with urllib.request.urlopen(req, timeout=120) as resp:
    body = json.loads(resp.read())
    print(json.dumps(body, indent=2))

print("[caller] done")
