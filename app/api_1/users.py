from . import api
from ..models import User,Post,Comment
from flask import jsonify,request,current_app,url_for

@api.route('/users/<int:id>')
def get_users(id):
    user=User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/users/<int:id>/posts')
def get_user_posts(id):
    user=User.query.get_or_404(id)
    page=request.args.get('page',1,type=int)
    pagination=user.posts.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False
    )
    posts=pagination.items
    prev=None
    if pagination.has_perv:
        prev=url_for('api.get_user_posts',page=page-1,_external=True)
    next=None
    if pagination.has_next:
        next=url_for('api.get_user_posts',page=page+1,_external=True)

    return jsonify({
        'posts':[post.to_json() for post in posts],
        'prev':prev,
        'next':next,
        'count':pagination.total
        })

@api.route('/users/<int:id>/timeline/')
def get_user_followed_post(id):
    user=User.query.get_or_404(id)
    page=request.args.get('page',1,type=int)
    pagination=user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False
    )
    posts=pagination.items
    prev=None
    if pagination.has_perv:
        prev=url_for('api.get_uer_followed_post',page=page-1,
                       _external=True)
    next=None
    if pagination.has_next:
        next=url_for('api.get_uer_followed_post',page=page+1,
                       _external=True)

    return jsonify({
        'posts':[post.to_json() for post in posts],
        'prev':prev,
        'next':next,
        'count':pagination.total
    })


