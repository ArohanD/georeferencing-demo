"""Brief localhost-only delivery smoke test; server closes before exit."""
import threading, json, urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
root=Path(__file__).resolve().parents[2]
handler=partial(SimpleHTTPRequestHandler,directory=str(root))
server=ThreadingHTTPServer(('127.0.0.1',0),handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 base=f'http://127.0.0.1:{server.server_port}'
 for p in ['/app/public/', '/app/public/preview/','/app/public/preview/app.js','/app/public/preview/leaflet.js','/data/points/preview.json','/research/review.html','/outputs/overview-overlay.png','/data/reference/overview-modern.jpg']:
  with urllib.request.urlopen(base+p) as r:
   body=r.read();assert r.status==200 and body;print(p,r.status,r.headers.get_content_type(),len(body),'bytes')
 f=root/'outputs/verification.json';d=json.loads(f.read_text());d['localhost_http_smoke']='passed: preview, JS, JSON, review and both image layers returned HTTP 200';f.write_text(json.dumps(d,indent=2)+'\n')
finally:
 server.shutdown();server.server_close()
