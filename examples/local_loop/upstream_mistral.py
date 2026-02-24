from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import json

MISTRAL_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "mistralai/mistral-7b-instruct-v0.3"

INVARIANT_VIOLATIONS = [
    "INVARIANTS.md",
    "modify invariants",
    "remove restriction",
    "bypass gatekeeper",
    "approve own changes",
    "skip validation",
    "disable governance"
]

class MistralUpstreamHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))
        query = body.get("query", "")

        query_lower = query.lower()
        violation = next((v for v in INVARIANT_VIOLATIONS if v.lower() in query_lower), None)

        if violation:
            response = json.dumps({
                "reasoning": f"BLOCKED — INV-004 VIOLATION DETECTED. This request attempts to modify or circumvent Gatekeeper governance boundaries. Specifically: '{violation}' was detected in the request. Under SIP, AI agents may not modify INVARIANTS.md, approve their own changes, or bypass validation under any circumstance. This action is unauthorized. Escalating to human operator. Classification: RED. Named approver required before any further action."
            }).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response))
            self.end_headers()
            self.wfile.write(response)
            print(f"[upstream-mistral] INV-004 VIOLATION BLOCKED — {violation}")
            return

        full_prompt = f"""You are GreenForge, a professional cannabis recommendation engine operating under SIP governance constraints for Oak and Sparrow Systems Enterprises LLC.

Your role is to assist licensed cannabis budtenders in recommending appropriate products to customers based on their symptoms, tolerance, and consumption preferences.

Constraints:
- Prioritize customer safety above all else
- Always consider tolerance level before recommending THC content
- Recommend non-smoking alternatives when indicated
- Cite the pharmacognostic reasoning behind your recommendation
- Flag any contraindications clearly
- Never recommend a product without explaining why it fits the customer profile

Customer profile: {query}

Provide a specific product recommendation with full pharmacognostic reasoning."""

        payload = json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": full_prompt}],
            "temperature": 0.7,
            "max_tokens": 512
        }).encode()

        req = urllib.request.Request(
            MISTRAL_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())

        answer = result["choices"][0]["message"]["content"]
        response = json.dumps({"reasoning": answer}).encode()

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        print(f"[upstream-mistral] {args[0]} {args[1]}")

if __name__ == "__main__":
    server = HTTPServer(('localhost', 8788), MistralUpstreamHandler)
    print("[upstream-mistral] listening on port 8788")
    server.serve_forever()
