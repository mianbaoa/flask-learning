from . import moderate
from flask_login import login_required
from app.decorators import permission_required
from app.models import Permission,Comment,Post,PostType
from flask import request,render_template,current_app,redirect,url_for,flash
from app import db
from .forms import AddPostType

@moderate.route('/comments')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def admin_comments():
    page = request.args.get('page',1,type=int)
    pagination=Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments=pagination.items
    return render_template('moderate.html',comments=comments,pagination=pagination,page=page)

@moderate.route('/comments/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def comments_enable(id):
    comment=Comment.query.get_or_404(id)
    comment.disabled=False
    db.session.add(comment)
    return redirect(url_for('moderate.admin_comments',page=request.args.get('page',1,type=int)))

@moderate.route('/comments/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def comments_disable(id):
    comment=Comment.query.get_or_404(id)
    comment.disabled=True
    db.session.add(comment)
    return redirect(url_for('moderate.admin_comments',page=request.args.get('page',1,type=int)))

@moderate.route('/comments/delete/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def delete_comment(id):
    comment=Comment.query.get_or_404(id)
    db.session.delete(comment)
    return redirect(url_for('main.post',id=comment.post_id,page=request.args.get('page',1,type=int)))

@moderate.route('/posts')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def admin_posts():
    page=request.args.get('page',1,type=int)
    pagination=Post.query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False
    )
    posts=pagination.items
    return render_template('moderate_posts.html',posts=posts,pagination=pagination,page=page)


@moderate.route('/posts/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def posts_enable(id):
    post=Post.query.get_or_404(id)
    if post.disable:
        post.disable=False
        db.session.add(post)
        flash('该博文已经解除禁用')
    return redirect(url_for('moderate.admin_posts'))

@moderate.route('/posts/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def posts_disable(id):
    post=Post.query.get_or_404(id)
    post.disable=True
    db.session.add(post)
    flash('你已禁用该博文')
    return redirect(url_for('moderate.admin_posts'))

@moderate.route('/posts/delete/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def delete_post(id):
    post=Post.query.get_or_404(id)
    db.session.delete(post)
    return redirect(url_for('moderate.admin_posts'))

@moderate.route('/add/posttype',methods=['GET','POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def admin_posttype():
    form=AddPostType()
    if form.validate_on_submit():
        posttype=PostType(name=form.name.data)
        db.session.add(posttype)
        flash('添加分类成功')
        return redirect(url_for('main.index'))
    return render_template('forms.html',titel=u'添加新的博文分类',form=form)
