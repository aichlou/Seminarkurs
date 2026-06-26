#!/usr/bin/env python3
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

PORT = 8080


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class StreamHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Logs unterdrücken

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
            <html><head>
            <title>RPi Kamera</title>
            <style>
                body { background: #111; display: flex; justify-content: center;
                       align-items: center; height: 100vh; margin: 0; }
                img  { max-width: 100%; border-radius: 8px; }
            </style>
            </head><body>
            <img src="/stream" />
            </body></html>
            """)

        elif self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()

            cmd = [
                'rpicam-vid',
                '--codec', 'mjpeg',
                '--width', '1280',
                '--height', '720',
                '--framerate', '30',
                '--timeout', '0',
                '-o', '-'
            ]

            proc = None
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                buf = b''
                while True:
                    chunk = proc.stdout.read(4096)
                    if not chunk:
                        break
                    buf += chunk
                    start = buf.find(b'\xff\xd8')
                    end = buf.find(b'\xff\xd9')
                    if start != -1 and end != -1 and end > start:
                        jpg = buf[start:end + 2]
                        buf = buf[end + 2:]
                        try:
                            self.wfile.write(
                                b'--frame\r\n'
                                b'Content-Type: image/jpeg\r\n\r\n'
                                + jpg + b'\r\n'
                            )
                        except BrokenPipeError:
                            break
            except Exception as e:
                print(f"Fehler: {e}")
            finally:
                if proc is not None:
                    proc.terminate()

        else:
            self.send_response(404)
            self.end_headers()


def main():
    print(f"Stream läuft auf http://<RPi-IP>:{PORT}")
    with ThreadingHTTPServer(('0.0.0.0', PORT), StreamHandler) as server:
        server.serve_forever()


if __name__ == '__main__':
    main()
