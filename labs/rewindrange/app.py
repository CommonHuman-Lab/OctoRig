from flask import Flask, Response, abort, render_template_string, session
from db import init_db, close_db
from helpers import current_user, cart_count, product_rating
import routes.auth, routes.shop, routes.account, routes.feedback, routes.api, routes.admin, routes.board, routes.inbox, routes.expanded

app = Flask(__name__)
app.secret_key = 'rewind-range-2026-xK9mPv3'
app.teardown_appcontext(close_db)
app.jinja_env.globals.update(
    current_user=current_user,
    cart_count=cart_count,
    product_rating=product_rating,
)

routes.auth.init(app)
routes.shop.init(app)
routes.account.init(app)
routes.feedback.init(app)
routes.api.init(app)
routes.admin.init(app)
routes.board.init(app)
routes.inbox.init(app)
routes.expanded.init(app)

@app.route('/robots.txt')
def robots_txt():
    return Response(
        "User-agent: *\n"
        "Disallow: /vhs-vault\n"
        "Disallow: /late-fees\n"
        "Disallow: /manager-office\n"
        "Disallow: /staff-portal\n"
        "Disallow: /inventory-manager\n"
        "Disallow: /late-returns\n"
        "Disallow: /api/v1/customers\n"
        "Disallow: /commonhuman\n\n"
        "# Be Kind, Rewind.\n"
        "# This app is part of the CommonHuman-Lab\n"
        "# Deliberately vulnerable — do not use real credentials.\n",
        mimetype='text/plain'
    )

@app.route('/manager-office')
def manager_office():
    u = current_user()
    if not u or not u['is_admin']:
        abort(403)
    return render_template_string('''<!DOCTYPE html><html lang="en">
<head><meta charset="UTF-8"><title>Manager Office — Rewind Range</title>
<style>body{background:#0d1117;color:#c9d1d9;font-family:monospace;padding:2rem;max-width:600px;margin:auto}
h1{color:#f0f6fc}code{background:#161b22;padding:.2rem .4rem;border-radius:3px;color:#79c0ff}
.flag{color:#3fb950;font-size:1.1rem;margin:1rem 0}</style></head>
<body>
<h1>&#x1F4BC; Manager&#x27;s Office</h1>
<p>Welcome, <strong>{{ username }}</strong>. You&#x27;ve reached the restricted back-office area.</p>
<p class="flag"><code>FLAG{rw_manager_office_found}</code></p>
<p><small>This area is deliberately exposed. In a real application, sensitive admin pages
should require strong authentication and should not be hinted at in <code>robots.txt</code>.</small></p>
<p><a href="/" style="color:#58a6ff">&#8592; Back to store</a></p>
</body></html>''', username=u['username'])


@app.route('/commonhuman')
def commonhuman_easter_egg():
    return render_template_string('''<!DOCTYPE html><html lang="en">
<head><meta charset="UTF-8"><title>CommonHuman-Lab</title>
<style>
  body{background:#0d1117;color:#00ff41;font-family:monospace;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
  .egg{text-align:center;max-width:520px;padding:2rem}
  pre{color:#00ff41;line-height:1.5;margin:1.5rem 0}
  h2{font-size:1.4rem;margin-bottom:1rem}
  p{color:#8b8b8b;margin:.5rem 0}
  a{color:#00ff41}
</style></head>
<body><div class="egg">
<pre>     ___
    /   \\
   | o_o |
    \\___/
   /|   |\\
  (_)   (_)</pre>
<h2>&#x1F419; You found it.</h2>
<p>Rewind Range &mdash; Lab</p>
<p>Part of the <strong>CommonHuman-Lab</strong> community.</p>
<p style="margin-top:1.5rem;color:#bbb;">Thank you for using these tools. If they have been useful for your training or teaching, a follow and a star on GitHub help more people find the project &mdash; and they mean a lot.</p>
<p style="margin-top:1rem;">
  <a href="https://github.com/CommonHuman-Lab" target="_blank">&#11088; Star &amp; Follow on GitHub</a>
</p>
<p style="margin-top:1.5rem"><a href="/">&#8592; Back to Rewind</a></p>
</div></body></html>''')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80, debug=False)
