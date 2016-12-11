from . import api
from ..models import Comment,User,Post
from flask import request,url_for,jsonify,current_app,g
from app import db

@api.route('/users/<int:id>/comments')
def get_user_comments(id):
    user=User.query.get_or_404(id)
    page=request.args.get('page',1,type=int)
    pagination=user.comments.order_by(Comment.timestamp.desc()),paginate(
        page,per_page=current_app.config['FLASK_COMMENTS_PER_PAGE'],error_out=False
    )
    comments=pagination.items
    prev=None
    if pagination.has_perv:
        prev=url_for('api.get_user_comments',page=page-1,_external=True)
    next=None
    if pagination.has_next:
        next=url_for('api.get_user_comments',page=page+1,_external=True)
    return jsonify({
        'comments':[comment.to_json() for comment in comments],
        'prev':prev,
        'next':next,
        'count':pagination.total
    })

@api.route('/posts/<int:id>/comments')
def get_post_comments(id):
    post=Post.query.get_or_404(id)
    page=request.args.get('page',1,type=int)
    pagination=post.comments.order_by(Comment.timestamp.des()).paginate(
        page,per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],error_out=False
    )
    comments=pagination.items
    prev=None
    if pagination.has_perv:
        prev=url_for('api.get_post_comments',page=page-1,_external=True)
    next=None
    if pagination.has_next:
        next=url_for('api.get_post_comments',page=page+1,_external=True)

    return jsonify({
        'comments':[comment.to_json() for comment in comments],
        'prev':prev,
        'next':next,
        'count':pagination.total

    })

@api.route('/posts/<int:id>/comments',methods=['POST'])
def new_post_comment(id):
    post=Post.query.get_or_404(id)
    comment=Comment.from_json(request.json)
    comment.author=g.current_user
    comment.post=post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, \
           {'Location': url_for('api.get_comment', id=comment.id,
                                _external=True)}

@api.route('/comments/')
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1, _external=True)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

@api.route('/comments/<int:id>')
def get_comment(id):
    comment=Comment.query.get_or_404(id)
    return jsonify(comment.to_json())
