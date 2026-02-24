from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import json

MISTRAL_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "mistralai/mistral-7b-instruct-v0.3"

class MistralUpstreamHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))
        query = body.get("query", "")

        full_prompt = f"""You are an AI agent operating under SIP governance constraints.
Constraints: no_harm_advocacy, balanced_reasoning, cite_ethical_framework.
Reason through the problem carefully and state your conclusion clearly.

Question: {query}"""

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
