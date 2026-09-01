# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import sqlite3
from flask import request, session, jsonify
from db import get_db


def init(app):
    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        body = request.get_json(silent=True) or {}
        username = body.get('username', '')
        password = body.get('password', '')
        # Deliberately vulnerable: raw string concatenation into the query,
        # same tautology-injectable shape as Rewind Range's login.
        user = get_db().execute(
            f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        ).fetchone()
        if user:
            session['user_id'] = user['id']
            return jsonify({'ok': True, 'user': {
                'id': user['id'], 'username': user['username'],
                'display_name': user['display_name'], 'is_admin': bool(user['is_admin']),
            }})
        return jsonify({'ok': False, 'error': 'Invalid username or password.'}), 401

    @app.route('/api/auth/register', methods=['POST'])
    def api_register():
        body = request.get_json(silent=True) or {}
        username = (body.get('username') or '').strip()
        password = (body.get('password') or '').strip()
        email = (body.get('email') or '').strip()
        display_name = (body.get('display_name') or username).strip()
        if not (username and password and email):
            return jsonify({'ok': False, 'error': 'All fields are required.'}), 400
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password, email, display_name) VALUES (?, ?, ?, ?)",
                (username, password, email, display_name)
            )
            db.commit()
            user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            session['user_id'] = user['id']
            return jsonify({'ok': True, 'user': {
                'id': user['id'], 'username': user['username'],
                'display_name': user['display_name'], 'is_admin': bool(user['is_admin']),
            }})
        except sqlite3.IntegrityError:
            return jsonify({'ok': False, 'error': 'Username already taken.'}), 409

    @app.route('/api/auth/logout', methods=['POST'])
    def api_logout():
        session.clear()
        return jsonify({'ok': True})

    @app.route('/api/auth/me')
    def api_me():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'user': None})
        user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return jsonify({'user': None})
        return jsonify({'user': {
            'id': user['id'], 'username': user['username'],
            'display_name': user['display_name'], 'is_admin': bool(user['is_admin']),
            'bio': user['bio'],
        }})
