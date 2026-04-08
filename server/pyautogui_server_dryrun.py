#!/usr/bin/env python3
"""Dry-run PyAutoGUI server — same API as pyautogui_server.py but logs
commands to server/cache/*.json instead of executing them.

No pyautogui or pyperclip dependency required.

Endpoints:
    POST /exec   — log a single action
    POST /batch  — log a batch of actions

Start:
    python3 server/pyautogui_server_dryrun.py              # default: 0.0.0.0:5000
    python3 server/pyautogui_server_dryrun.py --port 5001  # custom port
"""

import argparse
import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")

ALLOWED_HOSTS = {"127.0.0.1"}


def _save_to_cache(endpoint, body, client_ip):
    """Write a request to a timestamped JSON file in the cache directory."""
    now = datetime.now()
    entry = {
        "timestamp": now.isoformat(timespec="milliseconds"),
        "endpoint": endpoint,
        "body": body,
        "client": client_ip,
    }
    filename = now.strftime("%Y%m%d_%H%M%S_%f") + ".json"
    path = os.path.join(CACHE_DIR, filename)
    with open(path, "w") as f:
        json.dump(entry, f, indent=2)
    return path


class Handler(BaseHTTPRequestHandler):
    def _check_origin(self):
        client_ip = self.client_address[0]
        if ALLOWED_HOSTS and client_ip not in ALLOWED_HOSTS:
            self._respond(403, {"status": "error", "detail": f"Denied: {client_ip}"})
            return False
        return True

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        return json.loads(body)

    def _respond(self, code, data):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        if not self._check_origin():
            return

        try:
            body = self._read_json()
        except Exception as e:
            self._respond(400, {"status": "error", "detail": f"Bad JSON: {e}"})
            return

        if self.path == "/exec":
            self._handle_exec(body)
        elif self.path == "/batch":
            self._handle_batch(body)
        else:
            self._respond(404, {"status": "error", "detail": "Not found"})

    def _handle_exec(self, body):
        path = _save_to_cache("/exec", body, self.client_address[0])
        print(f"  [cached] /exec -> {os.path.basename(path)}")
        self._respond(200, {"status": "ok", "result": None})

    def _handle_batch(self, body):
        actions = body.get("actions", [])
        path = _save_to_cache("/batch", body, self.client_address[0])
        print(f"  [cached] /batch ({len(actions)} actions) -> {os.path.basename(path)}")
        self._respond(200, {"status": "ok", "results": [None] * len(actions)})

    def log_message(self, format, *args):
        print(f"[{self.client_address[0]}] {format % args}")


def main():
    parser = argparse.ArgumentParser(description="Dry-run PyAutoGUI server (logs to cache)")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=18271, help="Port (default 5000)")
    parser.add_argument("--allow", nargs="*", help="Allowed client IPs (default: 192.168.1.200)")
    args = parser.parse_args()

    if args.allow is not None:
        ALLOWED_HOSTS.clear()
        ALLOWED_HOSTS.update(args.allow)

    os.makedirs(CACHE_DIR, exist_ok=True)

    server = HTTPServer((args.host, args.port), Handler)
    print(f"PyAutoGUI DRY-RUN server listening on {args.host}:{args.port}")
    print(f"Cache directory: {CACHE_DIR}")
    print(f"Allowed clients: {ALLOWED_HOSTS or 'all'}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
