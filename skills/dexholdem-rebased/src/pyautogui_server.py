#!/usr/bin/env python3
"""PyAutoGUI remote server.

Runs on the remote machine (192.168.1.201) and accepts HTTP requests
from the client (192.168.1.200) to execute pyautogui/pyperclip actions.

Endpoints:
    POST /exec   — execute a single pyautogui action
    POST /batch  — execute a sequence of actions with optional sleeps

Start:
    python3 pyautogui_server.py              # default: 0.0.0.0:5000
    python3 pyautogui_server.py --port 8080  # custom port
"""

import argparse
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

import pyautogui

try:
    import pyperclip
except ImportError:
    pyperclip = None

# Disable pyautogui fail-safe pause
pyautogui.PAUSE = 0.05

ALLOWED_HOSTS = {"192.168.1.200"}


def _resolve_action(name):
    """Map an action name to a callable."""
    if name == "pyperclip.copy":
        if pyperclip is None:
            raise ValueError("pyperclip not installed")
        return pyperclip.copy
    if name == "pyperclip.paste":
        if pyperclip is None:
            raise ValueError("pyperclip not installed")
        return pyperclip.paste
    if name == "position":
        return pyautogui.position
    func = getattr(pyautogui, name, None)
    if func is None:
        raise ValueError(f"Unknown action: {name}")
    return func


def _exec_single(action_obj):
    """Execute one action dict, return result."""
    if "sleep" in action_obj:
        time.sleep(float(action_obj["sleep"]))
        return None

    name = action_obj["action"]
    args = action_obj.get("args", [])
    kwargs = action_obj.get("kwargs", {})
    func = _resolve_action(name)
    result = func(*args, **kwargs)

    # Convert pyautogui.Point to serializable form
    if hasattr(result, "x") and hasattr(result, "y"):
        return {"x": result.x, "y": result.y}
    return result


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
        try:
            result = _exec_single(body)
            self._respond(200, {"status": "ok", "result": result})
        except Exception as e:
            self._respond(500, {"status": "error", "detail": str(e)})

    def _handle_batch(self, body):
        actions = body.get("actions", [])
        results = []
        try:
            for i, action_obj in enumerate(actions):
                result = _exec_single(action_obj)
                results.append(result)
            self._respond(200, {"status": "ok", "results": results})
        except Exception as e:
            self._respond(500, {
                "status": "error",
                "detail": str(e),
                "completed": len(results),
            })

    def log_message(self, format, *args):
        print(f"[{self.client_address[0]}] {format % args}")


def main():
    parser = argparse.ArgumentParser(description="PyAutoGUI remote server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=5000, help="Port (default 5000)")
    parser.add_argument("--allow", nargs="*", help="Allowed client IPs (default: 192.168.1.200)")
    args = parser.parse_args()

    if args.allow is not None:
        ALLOWED_HOSTS.clear()
        ALLOWED_HOSTS.update(args.allow)

    server = HTTPServer((args.host, args.port), Handler)
    print(f"PyAutoGUI server listening on {args.host}:{args.port}")
    print(f"Allowed clients: {ALLOWED_HOSTS or 'all'}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
