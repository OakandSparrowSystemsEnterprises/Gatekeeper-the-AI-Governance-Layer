from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class UpstreamHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        response = {
            "recommendation": "Releaf Balm",
            "reason": "CBD ratio moderates THC effect for chronic pain topical application"
        }
        payload = json.dumps(response).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(payload))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        print(f"[upstream] {args[0]} {args[1]}")

if __name__ == "__main__":
    server = HTTPServer(('localhost', 8788), UpstreamHandler)
    print("[upstream] listening on port 8788")
    server.serve_forever()