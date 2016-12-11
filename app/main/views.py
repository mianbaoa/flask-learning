#创建视图文件很麻烦，仔细看看。
from flask import render_template,flash,redirect,url_for,make_response
from datetime import datetime
from . import main
from ..models import User,Role,Post,Comment
from flask import abort,request,current_app
from .forms import AddprofileForm,EditProfileAdminForm,PostForm,CommentForm
from flask_login import login_required,current_user
from app import db
from ..decorators import admin_required,permission_required
from ..models import Permission
from flask_sqlalchemy import get_debug_queries

@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration>=current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'slow query: %s\nParemeters: %s\nDuration: %f\nContext: %s\n' %
                (query.statement,query.parameters,query.duration,query.context))
    return response

@main.route('/',methods=['GET','POST'])
def index():
    form=PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post=Post(tit=form.titel.data,body=form.body.data,
                  author=current_user._get_current_object())#这里的_get_current_object是得到当前登录用户的整条属性
        db.session.add(post)
        return redirect(url_for('main.index'))
    show_followed=False
    if current_user.is_authenticated:
        show_followed=bool(request.cookies.get('show_followed',''))#第二个参数应该是默认值
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    page=request.args.get('page',1,type=int)
    pagination=query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    #这里返回的是一个列表,order_by时返回列表，应该是找寻所有有日期的文章,第一个参数为页数，第二个参数为每页的记录，第三个参数设为False，
    # 页数超出范围时会返回一个空列表
    posts=pagination.items#(这里items不懂什么意思)，应该表示为显示的结果吧
    return render_template('index.html',
                           current_time=datetime.utcnow(),show_followed=show_followed,form=form,posts=posts,pagination=pagination)

@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    post=Post.query.get_or_404(id)
    Post.add_view(post,db)
    form=CommentForm()
    if form.validate_on_submit():
        comment=Comment(body=form.body.data,
                        post=post
                        ,author=current_user._get_current_object())
        db.session.add(comment)
        flash('你的评论被添加到该博文')
        page = (post.comments.count() - 1) // \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1#这里是点完确定之后直接重定向到你的评论的那一页，这个是计算页数，
        #用//直接取整数部分，例：我评论的是第十条，则在第二页，而不是在第三页，一定要减一 ！逻辑很好理解
        return redirect(url_for('main.post',id=post.id,page=page))
    page = request.args.get('page' , 1, type=int)
    pagination=post.comments.order_by(Comment.timestamp.asc()).paginate(
        page,per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False
    )

    comments=pagination.items
    return render_template('post.html',posts=[post],comments=comments,pagination=pagination,form=form)

@main.route('/edit/<int:id>',methods=['GET','POST'])
def edit(id):
    post=Post.query.get_or_404(id)
    if current_user!=post.author and not current_user.can(Permission.WRITE_ARTICLES):
        abort(404)
    form=PostForm()
    if form.validate_on_submit():
        post.body=form.body.data
        db.session.add(post)
        flash('博文修改成功!!')
        return redirect(url_for('main.post',id=post.id))
    form.body.data=post.body
    form.titel.data=post.body
    return render_template('edit_post.html',form=form)

@main.route('/user/<username>')#这个视图函数不需要登录就可以访问，当登录用户为管理员时，想修改哪个用户就修改路由url后面的用户名字就行了
def user(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page=request.args.get('page',1,type=int)
    pagination=user.posts.order_by(Post.timestamp.desc()).paginate(page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                                   error_out=False)#这里返回一个列表，找寻一个用户的所有博文对象。这里很关键啊
    posts=pagination.items
    return render_template('user.html',user=user,posts=posts,pagination=pagination)

@main.route('/add-profile',methods=['GET','POST'])
@login_required
def add_profile():
    form=AddprofileForm()
    if form.validate_on_submit():
        current_user.name=form.name.data
        current_user.location=form.location.data
        current_user.about_me=form.about_me.data
        db.session.add(current_user)
        flash('个人信息已经更新')
        return redirect(url_for('main.user',username=current_user.username))
    form.name.data=current_user.name
    form.location.data=current_user.location
    form.about_me.data=current_user.about_me
    return render_template('add_profile.html',form=form)

@main.route('/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user=User.query.get_or_404(id)
    form=EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email=form.email.data
        user.username=form.username.data
        user.confirmed=form.confirmed.data
        user.role=Role.query.get(form.role.data)#这里role是要找寻id为输入id的Role角色
        user.name=form.name.data
        user.location=form.location.data
        user.about_me=form.about_me.data
        db.session.add(user)
        flash('用户资料已经更新')
        return redirect(url_for('main.user',username=user.username,user=user))
    form.email.data=user.email
    form.username.data=user.username
    form.confirmed.data=user.confirmed
    form.role.data=user.role_id
    form.name.data=user.name
    form.location.data=user.location
    form.about_me.data=user.about_me
    return render_template('add_profile.html',form=form,user=user)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('你关注的用户不存在')
        return redirect(url_for('main.user',username=username))
    if current_user.is_following(user):
        flash('你已经关注过该用户')
        return redirect(url_for('main.user',username=username))
    current_user.follow(user)
    flash('你已成功关注%s' %username)
    return redirect(url_for('main.user',username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('该用户不存在')
        return redirect(url_for('main.index'))
    if not user.is_followed_by(current_user):
        flash('你还没有关注该用户')
        return redirect(url_for('main.user',username=username))
    current_user.unfollow(user)
    flash('你已取消关注')
    return redirect(url_for('main.user',username=username))

@main.route('/followers/<username>',methods=['GET','POST'])
def followers(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('该用户不存在')
        return redirect(url_for('main.index'))
    page = request.args.get('page',1,type=int)
    pagination=user.followers.paginate(page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                       error_out=False)
    follows=[{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followed.html',follows=follows,pagination=pagination,user=user,
                           endpoint='main.followers',h2='的关注者',titel='Followers of')

@main.route('/followed/<username>',methods=['GET','POST'])
def followed(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('该用户不存在')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                         error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followed.html', follows=follows, pagination=pagination, user=user,
                           endpoint='main.followed',h2='关注了谁',titel='Followed of')

@main.route('/all',methods=['GET','POST'])
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))#创建响应对象
    resp.set_cookie('show_followed','',max_age=30*24*60*60)#设置一个月的cookie值，设置到cookie字典中
    return resp

@main.route('/followed',methods=['GET','POST'])
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp


@main.route('/shutdown')#关闭测试服务器的路由，只能在测试环境中使用
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown=request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down'





"""
@main.route('/moderate')
@login_required
@admin_required
def for_admins_only():
    return "For anministrators!"

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"
"""
