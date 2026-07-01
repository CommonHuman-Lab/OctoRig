from datetime import date
from flask import request, render_template, make_response, session, redirect, url_for, abort
from db import get_db
from helpers import current_user


def init(app):

    # ── Home ──────────────────────────────────────────────────────────────────

    @app.route('/')
    def index():
        db = get_db()
        featured_vhs   = db.execute(
            "SELECT * FROM products WHERE type='vhs'  ORDER BY RANDOM() LIMIT 5"
        ).fetchall()
        featured_games = db.execute(
            "SELECT * FROM products WHERE type='game' ORDER BY RANDOM() LIMIT 5"
        ).fetchall()
        return render_template('index.html',
                               featured_vhs=featured_vhs, featured_games=featured_games)

    # ── Browse — SQLi via genre / platform / type / year ─────────────────────

    @app.route('/browse')
    def browse():
        type_    = request.args.get('type', '').strip()
        platform = request.args.get('platform', '').strip()
        genre    = request.args.get('genre', '').strip()
        year     = request.args.get('year', '').strip()
        db = get_db()

        conditions = []
        if type_:
            conditions.append(f"type = '{type_}'")
        if platform:
            conditions.append(f"platform = '{platform}'")
        if genre:
            conditions.append(f"genre LIKE '%{genre}%'")
        if year:
            conditions.append(f"year = {year}")

        where    = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''
        products = db.execute(
            f"SELECT * FROM products {where} ORDER BY title"
        ).fetchall()
        genres    = db.execute(
            "SELECT DISTINCT genre FROM products ORDER BY genre"
        ).fetchall()
        platforms = db.execute(
            "SELECT DISTINCT platform FROM products WHERE platform IS NOT NULL ORDER BY platform"
        ).fetchall()

        return render_template('browse.html',
                               products=products, genre=genre,
                               type_=type_, platform=platform, year=year,
                               genres=genres, platforms=platforms)

    # ── Search — SQLi + reflected XSS via q ──────────────────────────────────

    @app.route('/search')
    def search():
        q  = request.args.get('q', '')
        db = get_db()
        results = db.execute(
            f"SELECT * FROM products "
            f"WHERE title LIKE '%{q}%' OR creator LIKE '%{q}%' OR genre LIKE '%{q}%' "
            f"ORDER BY title"
        ).fetchall() if q else []
        resp = make_response(render_template('search.html', results=results, q=q))
        # Non-HttpOnly cookie — readable via document.cookie (XSS challenge target)
        resp.set_cookie('xss_challenge', 'FLAG{rw_reflected_xss_fired}', httponly=False)
        return resp

    # ── Product detail + reviews — stored XSS via review text ────────────────

    @app.route('/product/<int:product_id>')
    def product(product_id):
        db = get_db()
        p  = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        if not p:
            abort(404)
        reviews = db.execute(
            "SELECT r.*, u.username FROM reviews r "
            "JOIN users u ON r.user_id = u.id "
            "WHERE r.product_id = ? ORDER BY r.review_date DESC",
            (product_id,)
        ).fetchall()
        return render_template('product.html', product=p, reviews=reviews)

    @app.route('/product/<int:product_id>/review', methods=['POST'])
    def submit_review(product_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db     = get_db()
        rating = int(request.form.get('rating', 3))
        text   = request.form.get('text', '').strip()
        if text:
            db.execute(
                "INSERT INTO reviews (product_id, user_id, rating, text, review_date) "
                "VALUES (?, ?, ?, ?, ?)",
                (product_id, session['user_id'], rating, text, str(date.today()))
            )
            db.commit()
        return redirect(url_for('product', product_id=product_id))

    # ── Cart — price accepted from client (price tampering) ──────────────────

    @app.route('/cart')
    def cart():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        items        = session.get('cart', [])
        subtotal     = round(sum(i['price'] for i in items), 2)
        coupon       = session.get('coupon')
        discount     = coupon['discount_pct'] if coupon else 0
        total        = round(subtotal * (1 - discount / 100), 2)
        coupon_error = session.pop('coupon_error', None)
        u = current_user()
        return render_template('cart.html', cart=items, subtotal=subtotal,
                               coupon=coupon, discount=discount, total=total,
                               coupon_error=coupon_error, u=u)

    @app.route('/cart/add', methods=['POST'])
    def cart_add():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        product_id = int(request.form.get('product_id', 0))
        price      = float(request.form.get('price', 0))
        p = get_db().execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        if not p:
            abort(404)
        cart = session.get('cart', [])
        cart.append({'product_id': product_id, 'title': p['title'],
                     'price': price, 'type': p['type']})
        session['cart'] = cart
        return redirect(url_for('cart'))

    @app.route('/cart/remove', methods=['POST'])
    def cart_remove():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        idx  = int(request.form.get('index', -1))
        cart = session.get('cart', [])
        if 0 <= idx < len(cart):
            cart.pop(idx)
        session['cart'] = cart
        return redirect(url_for('cart'))

    @app.route('/cart/coupon', methods=['POST'])
    def cart_coupon():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        code = request.form.get('code', '').strip()
        db   = get_db()
        try:
            row = db.execute(
                f"SELECT * FROM coupons WHERE code = '{code}'"
            ).fetchone()
        except Exception as e:
            session['coupon_error'] = str(e)
            return redirect(url_for('cart'))
        if row:
            session['coupon'] = {
                'code': row['code'],
                'discount_pct': row['discount_pct'],
                'description': row['description'],
            }
            session.pop('coupon_error', None)
        else:
            session['coupon_error'] = f'Coupon code "{code}" is not valid.'
            session.pop('coupon', None)
        return redirect(url_for('cart'))

    @app.route('/cart/clear', methods=['POST'])
    def cart_clear():
        session.pop('cart', None)
        session.pop('coupon', None)
        return redirect(url_for('cart'))

    # ── Checkout ──────────────────────────────────────────────────────────────

    @app.route('/checkout')
    def checkout():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        items    = session.get('cart', [])
        if not items:
            return redirect(url_for('browse'))
        subtotal = round(sum(i['price'] for i in items), 2)
        coupon   = session.get('coupon')
        discount = coupon['discount_pct'] if coupon else 0
        total    = round(subtotal * (1 - discount / 100), 2)
        u = current_user()
        return render_template('checkout.html', cart=items, subtotal=subtotal,
                               coupon=coupon, discount=discount, total=total, u=u)

    @app.route('/checkout/complete', methods=['POST'])
    def checkout_complete():
        uid = session.get('user_id')
        if not uid:
            return redirect(url_for('login'))
        items = session.get('cart', [])
        if not items:
            return redirect(url_for('browse'))

        subtotal = round(sum(i['price'] for i in items), 2)
        coupon   = session.get('coupon')
        discount = coupon['discount_pct'] if coupon else 0
        total    = round(subtotal * (1 - discount / 100), 2)

        db = get_db()
        u  = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()

        if u['balance'] < total:
            return render_template('checkout.html', cart=items, subtotal=subtotal,
                                   coupon=coupon, discount=discount, total=total, u=u,
                                   error='Insufficient balance on your membership card.')

        db.execute(
            "INSERT INTO orders (user_id, order_date, status, total, shipping_address) "
            "VALUES (?, ?, ?, ?, ?)",
            (uid, str(date.today()), 'processing', total, u['address'])
        )
        order_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        for item in items:
            db.execute(
                "INSERT INTO order_items (order_id, product_id, price) VALUES (?, ?, ?)",
                (order_id, item['product_id'], item['price'])
            )

        db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (total, uid))
        db.commit()

        session.pop('cart', None)
        session.pop('coupon', None)
        session.pop('coupon_error', None)

        return redirect(url_for('order', order_id=order_id))
