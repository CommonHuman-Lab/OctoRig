# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import Flask, Response
from db import init_db, close_db
import routes.auth, routes.api, routes.admin, routes.social

app = Flask(__name__)
app.secret_key = 'waveform-tR7nQz2'
app.teardown_appcontext(close_db)

routes.auth.init(app)
routes.api.init(app)
routes.admin.init(app)
routes.social.init(app)

SHELL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Waveform</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<div id="app"></div>
<script type="module" src="/static/app.js"></script>
</body>
</html>"""


@app.route('/robots.txt')
def robots_txt():
    return Response(
        "User-agent: *\n"
        "Disallow: /admin\n"
        "Disallow: /api/admin\n\n"
        "# Waveform — deliberately vulnerable, part of CommonHuman-Lab.\n"
        "# Do not use real credentials.\n",
        mimetype='text/plain'
    )


@app.route('/commonhuman')
def commonhuman_easter_egg():
    return Response("""<!DOCTYPE html><html lang="en">
<head><meta charset="UTF-8"><title>CommonHuman-Lab</title>
<style>
  body{background:#0d1117;color:#00ff9d;font-family:monospace;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
  .egg{text-align:center;max-width:520px;padding:2rem}
  pre{color:#00ff9d;line-height:1.5;margin:1.5rem 0}
  h2{font-size:1.4rem;margin-bottom:1rem}
  p{color:#8b8b8b;margin:.5rem 0}
  a{color:#00ff9d}
</style></head>
<body><div class="egg">
<pre>  )))
 )))
)))
&#9834;</pre>
<h2>You found it.</h2>
<p>Waveform &mdash; Lab</p>
<p>Part of the <strong>CommonHuman-Lab</strong> community.</p>
<p style="margin-top:1rem;">
  <a href="https://github.com/CommonHuman-Lab" target="_blank">Star &amp; Follow on GitHub</a>
</p>
<p style="margin-top:1.5rem"><a href="/">&#8592; Back to Waveform</a></p>
</div></body></html>""", mimetype='text/html')


@app.route('/')
@app.route('/<path:path>')
def spa_shell(path=None):
    return Response(SHELL_HTML, mimetype='text/html')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80, debug=False, threaded=True)
