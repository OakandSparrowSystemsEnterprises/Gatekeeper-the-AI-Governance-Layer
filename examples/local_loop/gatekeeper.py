from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import hashlib
import json
import datetime
import os

ARTIFACT_LOG = "artifacts\\gatekeeper.ndjson"

SIP_POLICY = {
    "policy_id": "sip-gatekeeper-v1.0",
    "mode": "observe",
    "constraints": [
        "INV-001:human_escalation_required_for_red",
        "INV-002:declaration_before_action",
        "INV-003:audit_log_append_only",
        "INV-005:scope_boundaries_enforced",
        "INV-007:risk_classification_mandatory"
    ],
    "classification": "GREEN",
    "authority": "Oak and Sparrow Systems Enterprises LLC"
}

def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()

def load_prev_hash() -> str:
    try:
        with open(ARTIFACT_LOG, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
            if lines:
                last = json.loads(lines[-1])
                return last["chain"]["this_hash"]
    except FileNotFoundError:
        pass
    return "sha256:" + "0" * 64

def get_next_idx() -> int:
    if not os.path.exists(ARTIFACT_LOG):
        return 1
    with open(ARTIFACT_LOG, "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    return len(lines) + 1

def write_artifact(record: dict):
    with open(ARTIFACT_LOG, "a") as f:
        f.write(json.dumps(record) + "\n")

class GatekeeperHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        req_body = self.rfile.read(length)
        req_hash = sha256(req_body)

        upstream_req = urllib.request.Request(
            "http://localhost:8788" + self.path,
            data=req_body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(upstream_req, timeout=120) as resp:
            res_body = resp.read()
            status = resp.status

        res_hash = sha256(res_body)
        prev_hash = load_prev_hash()

        record = {
            "idx": get_next_idx(),
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "actor": {
                "type": "agent",
                "name": "mistral-7b-instruct",
                "instance_id": "devbox-001",
                "authority": "Oak and Sparrow Systems Enterprises LLC"
            },
            "policy_envelope": SIP_POLICY,
            "operation": {
                "kind": "http.request",
                "method": "POST",
                "path": self.path,
                "request_hash": req_hash,
                "inputs": json.loads(req_body)
            },
            "system_response": {
                "status": status,
                "response_hash": res_hash,
                "outputs": json.loads(res_body)
            },
            "chain": {
                "prev_hash": prev_hash,
                "this_hash": ""
            }
        }

        record["chain"]["this_hash"] = sha256(
            json.dumps({**record, "chain": {"prev_hash": prev_hash, "this_hash": ""}},
            sort_keys=True).encode()
        )

        write_artifact(record)
        print(f"[gatekeeper] artifact written — idx:{record['idx']} policy:sip-gatekeeper-v1.0 this_hash:{record['chain']['this_hash'][:30]}...")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(res_body))
        self.end_headers()
        self.wfile.write(res_body)

    def log_message(self, format, *args):
        print(f"[gatekeeper] {args[0]} {args[1]}")

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8787), GatekeeperHandler)
    print("[gatekeeper] listening on port 8787 — sip-gatekeeper-v1.0 active")
    server.serve_forever()
