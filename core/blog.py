from flask import(
	Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort 

from core.auth import login_required
from core.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
	db = get_db()
	posts = db.execute(
		'SELECT p.id , title, body, created, author_id, username, likes, dislikes'
		' FROM post p JOIN user u ON p.author_id = u.id'
		' ORDER BY created DESC'
	).fetchall()
	return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']
		error = None 

		if not title:
			error = 'Title is required.'
		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
				'INSERT INTO post (title, body, author_id)'
				' VALUES (?,?,?)',
				(title, body, g.user['id'])
			)
			db.commit()
			return redirect(url_for('blog.index'))

	return render_template('blog/create.html')

def get_post(id, check_author=True):
	post = get_db().execute(
		'SELECT p.id, title, body, created, author_id, username, likes, dislikes'
		' FROM post p JOIN user u ON p.author_id = u.id'
		' WHERE p.id = ?',
		(id,)
	).fetchone()

	if post is None:
		abort(404, 'Post id {0} doesn\'t exist.'.format(id))

	if check_author and post['author_id'] != g.user['id']:
		abort(403)

	return post 

@bp.route('/<int:id>/update', methods=('GET','POST'))
@login_required
def update(id):
	post = get_post(id)

	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']
		error = None 

		if not title:
			error = 'Title is required.'

		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
				'UPDATE post SET title = ?, body = ?'
				' WHERE id = ?',
				(title, body, id)
			)
			db.commit()
			return redirect(url_for('blog.index'))

	return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods = ('POST',))
@login_required
def delete(id):
	get_post(id)
	db = get_db()
	db.execute('DELETE FROM post WHERE id = ?', (id,))
	db.commit()
	return redirect(url_for('blog.index'))


@bp.route('/add_comment/<int:id>', methods = ('POST', ))
@login_required
def add_comment(id):
	if request.method == 'POST':
		body = request.form['body']
		error = None 
		post = get_post(id)
		if not body:
			error = 'Body is required.'
		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
				'INSERT INTO comment (body_com, author_id_com, post_id)'
				' VALUES (?,?,?)',
				(body, g.user['id'], id)
			)
			db.commit()
			return redirect(url_for('blog.detail', id = post['id']))

	return render_template('blog/post.html')




@bp.route('/<int:id>/detail', methods=('GET','POST',))
def detail(id):
	post = get_post(id)
	com = get_db().execute(
		'SELECT c.id, body_com, created_com, author_id, post_id,  created'
		' FROM comment c JOIN post p ON c.post_id = p.id'
		' ORDER BY created DESC'
	).fetchall()
	eror = None
	if not post:
		error = 'Not post'

	return render_template('blog/post.html', post=post, comments = com)



@bp.route('/<int:id>/like', methods=('POST',))
@login_required 
def like(id):
	post = get_post(id)
	likes =  post['likes'] + 1
	db = get_db()
	db.execute('UPDATE post SET likes = ?'
		'WHERE id = ?',
		(likes, id))
	db.commit()

	return redirect(url_for('blog.detail', id=post['id']))

@bp.route('/<int:id>/dislike', methods=('POST',))
@login_required 
def dislike(id):
	post = get_post(id)
	dislikes =  post['dislikes'] + 1
	db = get_db()
	db.execute('UPDATE post SET dislikes = ?'
		'WHERE id = ?',
		(dislikes, id))
	db.commit()
	return redirect(url_for('blog.detail', id=post['id']))

