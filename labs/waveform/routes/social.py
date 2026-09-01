# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import session, jsonify
from db import get_db


def init(app):
    # IDOR: requires *a* login but never checks it matches user_id.
    @app.route('/api/users/<int:user_id>/recent')
    def api_user_recent(user_id):
        if not session.get('user_id'):
            return jsonify({'error': 'not authenticated'}), 401
        rows = get_db().execute(
            "SELECT plays.id, plays.played_at, plays.note, tracks.title, tracks.duration_sec "
            "FROM plays JOIN tracks ON tracks.id = plays.track_id "
            "WHERE plays.user_id = ? ORDER BY plays.played_at DESC", (user_id,)
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    # IDOR: same missing ownership check as above.
    @app.route('/api/users/<int:user_id>/following')
    def api_user_following(user_id):
        if not session.get('user_id'):
            return jsonify({'error': 'not authenticated'}), 401
        rows = get_db().execute(
            "SELECT follows.id, follows.note, artists.id AS artist_id, artists.name AS artist_name "
            "FROM follows JOIN artists ON artists.id = follows.artist_id "
            "WHERE follows.user_id = ? ORDER BY follows.id", (user_id,)
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    # Not a vuln: always writes against the session's own user_id.
    @app.route('/api/artists/<int:artist_id>/follow', methods=['POST'])
    def api_follow_artist(artist_id):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'not authenticated'}), 401
        db = get_db()
        existing = db.execute(
            "SELECT id FROM follows WHERE user_id = ? AND artist_id = ?", (user_id, artist_id)
        ).fetchone()
        if existing:
            db.execute("DELETE FROM follows WHERE id = ?", (existing['id'],))
            following = False
        else:
            db.execute("INSERT INTO follows (user_id, artist_id, note) VALUES (?, ?, '')",
                       (user_id, artist_id))
            following = True
        db.commit()
        count = db.execute("SELECT COUNT(*) AS n FROM follows WHERE artist_id = ?",
                            (artist_id,)).fetchone()['n']
        return jsonify({'following': following, 'follower_count': count})

    # Public — safe to expose without auth.
    @app.route('/api/artists/<int:artist_id>/followers/count')
    def api_artist_follower_count(artist_id):
        count = get_db().execute(
            "SELECT COUNT(*) AS n FROM follows WHERE artist_id = ?", (artist_id,)
        ).fetchone()['n']
        return jsonify({'follower_count': count})
