"""Offline synthetic preview only: no HA, model, control, or network client."""

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import re
from socketserver import TCPServer


def create_server(index_path, bind=("127.0.0.1", 0), *, trusted_proxy_ip="172.30.32.2"):
    """Read both bounded page snapshots before binding; trust injection is for tests.

    The peer/identity check establishes authenticated ingress preview access,
    not an independently verified Home Assistant administrator role.
    """
    pages = {}
    for route, path in (("/index.html", Path(index_path)),
                        ("/devicebook.html", Path(index_path).with_name("devicebook.html"))):
        with path.open("rb") as source:
            page = source.read(1048577)
        if len(page) > 1048576:
            raise ValueError("Preview page exceeds 1 MiB")
        pages[route] = page
    pages["/"] = pages["/index.html"]

    class PreviewHandler(BaseHTTPRequestHandler):
        # One process, no worker pool; stalled accepted sockets cannot wait forever.
        timeout = 1.0

        def log_message(self, format, *args):
            # Paths, identities and parser errors must not enter request logs.
            pass

        def version_string(self):
            return "LUMO preview"

        def send_error(self, code, message=None, explain=None):
            # The stdlib's error pages include caller-controlled protocol text.
            self.close_connection = True
            if code == 501:  # Base handler dispatches every unsupported method here.
                self._reply(405, b"Method not allowed\n", "text/plain; charset=utf-8")
            else:
                self._reply(code, b"Request rejected\n", "text/plain; charset=utf-8")

        def _reply(self, status, body, content_type="text/html; charset=utf-8"):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            if status == 405:
                self.send_header("Allow", "GET, HEAD")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Frame-Options", "SAMEORIGIN")
            # This directive supplements, rather than replaces, the HTML's CSP.
            self.send_header("Content-Security-Policy", "frame-ancestors 'self'")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def do_GET(self):
            # BaseHTTPRequestHandler folds leading //; validate the raw target.
            target = self.requestline.split()[1]
            if target == "/health":
                self._reply(200, b"ok\n", "text/plain; charset=utf-8")
                return
            if target not in pages:
                self._reply(404, b"Not found\n", "text/plain; charset=utf-8")
                return
            identities = self.headers.get_all("X-Remote-User-Id", [])
            if (self.client_address[0] != trusted_proxy_ip
                    or len(identities) != 1
                    or re.fullmatch(r"[A-Za-z0-9_-]{1,128}", identities[0]) is None):
                self._reply(403, b"Forbidden\n", "text/plain; charset=utf-8")
                return
            self._reply(200, pages[target])

        do_HEAD = do_GET

    # HTTPServer.server_bind performs a DNS lookup, which can stall offline boot.
    server = HTTPServer(bind, PreviewHandler, bind_and_activate=False)
    try:
        TCPServer.server_bind(server)
        server.server_name, server.server_port = server.server_address
        server.server_activate()
    except BaseException:
        server.server_close()
        raise
    return server


def main():
    """Fixed Supervisor ingress entrypoint; no CLI/environment trust overrides."""
    with create_server(Path(__file__).with_name("index.html"),
                       bind=("0.0.0.0", 8099), trusted_proxy_ip="172.30.32.2") as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
