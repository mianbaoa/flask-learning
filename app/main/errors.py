from . import main
from flask import render_template,request,jsonify

@main.errorhandler(404)
def error_notfound(e):
    if request.accept_mimetypes.accept_json and \
        not request.accept_mimetypes.accept_html:
        response=jsonify({'error': 'not found'})
        response.status_code=404
    return render_template('404.html'),404

@main.errorhandler(500)
def error_Internet(e):
    if request.accept_mimetypes.accept_json and \
        not request.accept_mimetypes.accept_html:
        response=jsonify({'error': 'internal server error'})
        response.status_code=500
    return render_template('500.html'),500

@main.errorhandler(403)
def error_ban(e):
    return render_template('403.html'),403
