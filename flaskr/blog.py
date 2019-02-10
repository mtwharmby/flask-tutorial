from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import sys

bp = Blueprint('blog', __name__)  # No url_prefix, so all views relative to /


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
        ).fetchall()
    # Passing the argument posts to index.html
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    print('Method: {}'.format(request.method), file=sys.stderr)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('INSERT INTO post (title, body, author_id)'
                       ' VALUES (?, ?, ?)',
                       (title, body, g.user['id']))
            db.commit()

            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute('SELECT p.id, title, body, created, author_id,'
                            ' username FROM post p JOIN user u ON'
                            ' p.author_id = u.id WHERE p.id = ?',
                            (id,)).fetchone()

    if post is None:
        abort(404, 'Post id {0} does not exist'.format(id))
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


# N.B. following route passes an argument to the method (typed checked int)
# Without the int, it would be passed as a string.
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('UPDATE post SET title = ?, body = ? WHERE id = ?',
                       (title, body, id))
            db.commit()

        return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


# Delete functionality is part of update.html. As no template for this, while '
# have no post method
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)  # We don't actually need to post, but need to know if exists
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))