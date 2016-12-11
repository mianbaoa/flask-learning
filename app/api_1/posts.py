from . import api
from app.auth import auth
from app.models import Post
from flask import request,g,jsonify,url_for,current_app
from flask_login import login_required
from .decorators import permission_required
from app.models import Permission
from .errors import forbidden
from .. import db


@api.route('/posts/',methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post=Post.from_json(request.json)#请求中包含的JSON数据可通过request.json这个字典获取
    post.author=g.current_user#每次请求时用作临时储存的对象，每次请求都会重设这个变量
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()),201,{'Location':url_for('api.get_post',id=post.id,_external=True)}

@api.route('/posts/',methods=['GET'])#文章请求GET的处理程序
def get_posts():
    page = request.args.get('page',1,type=int)
    pagination=Post.query.paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    posts=pagination.items
    prev=None
    if pagination.has_prev:
        prev=url_for('api.get_posts',page=page - 1,_external=True)
    next=None
    if pagination.has_next:
        next=url_for('api.get_posts',page=page + 1,_external=True)
    return jsonify({
        'posts':[post.to_json() for post in posts],
        'prev':prev,
        'next':next,
        'count':pagination.total
    })

@api.route('/posts/<int:id>',methods=['GET'])
def get_post(id):
    post=Post.query.get_or_404(id)
    return jsonify(post.to_json())

@api.route('/posts/<int:id>',methods=['PUT'])#文章资源PUT请求的处理程序
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post=Post.query.get_or_404(id)
    if g.current_user!=post.author and not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    post.body=request.json.get('body',post.body)#后面参数应该是默认值，
    # 意思是如果json请求中body为空及默认为post.body不变。
    db.session.add(post)
    return jsonify(post.to_json())



