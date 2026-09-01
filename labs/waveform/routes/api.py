# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import request, session, jsonify
from db import get_db


def init(app):
    @app.route('/api/artists')
    def api_artists():
        rows = get_db().execute("SELECT id, name, genre FROM artists ORDER BY name").fetchall()
        return jsonify([dict(r) for r in rows])

    @app.route('/api/artists/<int:artist_id>')
    def api_artist_detail(artist_id):
        db = get_db()
        artist = db.execute("SELECT * FROM artists WHERE id = ?", (artist_id,)).fetchone()
        if not artist:
            return jsonify({'error': 'not found'}), 404
        albums = db.execute(
            "SELECT id, title, year FROM albums WHERE artist_id = ? ORDER BY year", (artist_id,)
        ).fetchall()
        top_tracks = db.execute(
            "SELECT tracks.id, tracks.title, tracks.duration_sec, albums.title AS album_title "
            "FROM tracks JOIN albums ON albums.id = tracks.album_id "
            "WHERE albums.artist_id = ? ORDER BY tracks.id LIMIT 5", (artist_id,)
        ).fetchall()
        return jsonify({
            'artist': dict(artist),
            'albums': [dict(a) for a in albums],
            'top_tracks': [dict(t) for t in top_tracks],
        })

    # IDOR: no authentication or ownership check at all — any visitor can pull
    # any artist's private royalty statement, including the payout memo.
    @app.route('/api/artists/<int:artist_id>/royalties')
    def api_artist_royalties(artist_id):
        rows = get_db().execute(
            "SELECT period, amount, memo FROM royalties WHERE artist_id = ?", (artist_id,)
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    @app.route('/api/albums/<int:album_id>')
    def api_album_detail(album_id):
        db = get_db()
        album = db.execute(
            "SELECT albums.*, artists.name AS artist_name FROM albums "
            "JOIN artists ON artists.id = albums.artist_id WHERE albums.id = ?", (album_id,)
        ).fetchone()
        if not album:
            return jsonify({'error': 'not found'}), 404
        tracks = db.execute(
            "SELECT id, title, duration_sec FROM tracks WHERE album_id = ?", (album_id,)
        ).fetchall()
        return jsonify({'album': dict(album), 'tracks': [dict(t) for t in tracks]})

    @app.route('/api/playlists/featured')
    def api_playlists_featured():
        rows = get_db().execute(
            "SELECT playlists.id, playlists.title, playlists.description, users.display_name AS owner "
            "FROM playlists JOIN users ON users.id = playlists.user_id "
            "WHERE playlists.is_private = 0 ORDER BY playlists.id"
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    # IDOR: private playlists are returned to anyone who guesses the id —
    # is_private is stored but never checked here.
    @app.route('/api/playlists/<int:playlist_id>')
    def api_playlist_detail(playlist_id):
        db = get_db()
        playlist = db.execute(
            "SELECT playlists.*, users.display_name AS owner FROM playlists "
            "JOIN users ON users.id = playlists.user_id WHERE playlists.id = ?", (playlist_id,)
        ).fetchone()
        if not playlist:
            return jsonify({'error': 'not found'}), 404
        tracks = db.execute(
            "SELECT tracks.id, tracks.title, tracks.duration_sec, albums.title AS album_title, "
            "artists.id AS artist_id, artists.name AS artist_name "
            "FROM playlist_tracks "
            "JOIN tracks ON tracks.id = playlist_tracks.track_id "
            "JOIN albums ON albums.id = tracks.album_id "
            "JOIN artists ON artists.id = albums.artist_id "
            "WHERE playlist_tracks.playlist_id = ?", (playlist_id,)
        ).fetchall()
        return jsonify({'playlist': dict(playlist), 'tracks': [dict(t) for t in tracks]})

    @app.route('/api/playlists/mine')
    def api_playlists_mine():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'not authenticated'}), 401
        rows = get_db().execute(
            "SELECT id, title, description, is_private FROM playlists WHERE user_id = ? ORDER BY id",
            (user_id,)
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    @app.route('/api/playlists', methods=['POST'])
    def api_playlists_create():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'not authenticated'}), 401
        body = request.get_json(silent=True) or {}
        title = (body.get('title') or '').strip()
        if not title:
            return jsonify({'error': 'title required'}), 400
        db = get_db()
        cur = db.execute(
            "INSERT INTO playlists (user_id, title, description, is_private) VALUES (?, ?, ?, ?)",
            (user_id, title, body.get('description') or '', 1 if body.get('is_private') else 0)
        )
        db.commit()
        return jsonify({'ok': True, 'id': cur.lastrowid})

    # IDOR: adding a track checks that you're logged in, but never that the
    # playlist you're adding to actually belongs to you.
    @app.route('/api/playlists/<int:playlist_id>/tracks', methods=['POST'])
    def api_playlist_add_track(playlist_id):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'not authenticated'}), 401
        body = request.get_json(silent=True) or {}
        track_id = body.get('track_id')
        if not track_id:
            return jsonify({'error': 'track_id required'}), 400
        db = get_db()
        playlist = db.execute("SELECT user_id FROM playlists WHERE id = ?", (playlist_id,)).fetchone()
        if not playlist:
            return jsonify({'error': 'not found'}), 404
        db.execute("INSERT INTO playlist_tracks (playlist_id, track_id) VALUES (?, ?)",
                   (playlist_id, track_id))
        db.commit()
        result = {'ok': True}
        if playlist['user_id'] != user_id:
            result['flag'] = 'FLAG{wf_playlist_mutate_idor}'
        return jsonify(result)

    # IDOR: same missing ownership check on removal — anyone logged in can
    # delete tracks from a playlist they don't own.
    @app.route('/api/playlists/<int:playlist_id>/tracks/<int:track_id>', methods=['DELETE'])
    def api_playlist_remove_track(playlist_id, track_id):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'not authenticated'}), 401
        db = get_db()
        playlist = db.execute("SELECT user_id FROM playlists WHERE id = ?", (playlist_id,)).fetchone()
        if not playlist:
            return jsonify({'error': 'not found'}), 404
        db.execute("DELETE FROM playlist_tracks WHERE playlist_id = ? AND track_id = ?",
                   (playlist_id, track_id))
        db.commit()
        result = {'ok': True}
        if playlist['user_id'] != user_id:
            result['flag'] = 'FLAG{wf_playlist_mutate_idor}'
        return jsonify(result)

    # IDOR: deleting a whole playlist checks login only, never ownership.
    # There is deliberately no delete button in the UI for this — the account
    # and playlist pages only expose track-level add/remove — so this route
    # is reachable only by calling the API directly.
    @app.route('/api/playlists/<int:playlist_id>', methods=['DELETE'])
    def api_playlist_delete(playlist_id):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'not authenticated'}), 401
        db = get_db()
        playlist = db.execute("SELECT user_id FROM playlists WHERE id = ?", (playlist_id,)).fetchone()
        if not playlist:
            return jsonify({'error': 'not found'}), 404
        db.execute("DELETE FROM playlist_tracks WHERE playlist_id = ?", (playlist_id,))
        db.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
        db.commit()
        result = {'ok': True}
        if playlist['user_id'] != user_id:
            result['flag'] = 'FLAG{wf_playlist_delete_idor}'
        return jsonify(result)

    # SQLi: q is concatenated straight into the query, UNION-injectable to
    # pull rows from _flags or users. Deliberately mirrors Rewind Range's
    # browse-filter injection shape.
    @app.route('/api/search')
    def api_search():
        q = request.args.get('q', '')
        db = get_db()
        try:
            rows = db.execute(
                "SELECT tracks.id, tracks.title AS title, albums.title AS subtitle "
                "FROM tracks JOIN albums ON albums.id = tracks.album_id "
                f"WHERE tracks.title LIKE '%{q}%'"
            ).fetchall()
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        return jsonify([dict(r) for r in rows])

    @app.route('/api/account', methods=['GET', 'POST'])
    def api_account():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'not authenticated'}), 401
        db = get_db()
        escalated = False
        if request.method == 'POST':
            body = request.get_json(silent=True) or {}
            display_name = body.get('display_name')
            bio = body.get('bio')
            # Stored XSS: display_name/bio are persisted verbatim and later
            # rendered client-side via innerHTML with no escaping.
            if display_name is not None:
                db.execute("UPDATE users SET display_name = ? WHERE id = ?", (display_name, user_id))
            if bio is not None:
                db.execute("UPDATE users SET bio = ? WHERE id = ?", (bio, user_id))
            # Mass assignment: is_admin is honored straight off the request
            # body with no allow-list or role check.
            if 'is_admin' in body:
                db.execute("UPDATE users SET is_admin = ? WHERE id = ?",
                           (1 if body.get('is_admin') else 0, user_id))
                escalated = bool(body.get('is_admin'))
            db.commit()
        user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        result = dict(user)
        if escalated:
            result['flag'] = 'FLAG{wf_mass_assignment_privilege_escalation}'
        return jsonify(result)

    # Broken access control: checks that *someone* is logged in, but never
    # checks is_admin — any authenticated user reaches the admin stats.
    @app.route('/api/admin/stats')
    def api_admin_stats():
        if not session.get('user_id'):
            return jsonify({'error': 'not authenticated'}), 401
        db = get_db()
        user_count = db.execute("SELECT COUNT(*) AS n FROM users").fetchone()['n']
        playlist_count = db.execute("SELECT COUNT(*) AS n FROM playlists").fetchone()['n']
        return jsonify({
            'user_count': user_count,
            'playlist_count': playlist_count,
            'flag': 'FLAG{wf_admin_api_no_authz_check}',
        })
