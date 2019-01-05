from flask import abort
from flask import flash
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import session as flask_session
from models import Category
from models import Item
from models import session
from models import User
import random
import string


app = Flask(__name__)


app.jinja_env.globals.update(
    is_authenticated=lambda: hasattr(app, 'current_user'))


def set_csrf_token():
    """Sets a new csrf_token to the user-session and returns it.
    """
    csrf_token = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))

    flask_session['csrf_token'] = csrf_token
    return csrf_token


def validate_csrf_token(token):
    """Validates the given csrf-token with the token stored within the
    user-session.
    """
    return flask_session['csrf_token'] == token


@app.route('/catalog.json')
def catalog_json_view():
    categories = session.query(Category).all()

    return jsonify(
        {'categories': [category.as_dict() for category in categories]})


@app.route('/')
def dashboard():
    categories = session.query(Category).all()
    items = session.query(Item).order_by('creation_date desc').limit(10).all()

    return render_template('dashboard.html', categories=categories, items=items)


@app.route('/categories/<string:category_title>')
def category_view(category_title):
    categories_query = session.query(Category)
    categories = categories_query.all()
    category = categories_query.filter_by(title=category_title).first()

    if not category:
        return abort(404)
    return render_template('category.html',
                           categories=categories, category=category)


@app.route('/categories/<string:category_title>/<string:item_title>')
def item_view(category_title, item_title):
    item = session.query(Item).filter_by(title=item_title).first()
    if not item:
        return abort(404)
    return render_template('item.html', item=item)


@app.route('/categories/<string:category_title>/<string:item_title>/edit')
def item_edit_view(category_title, item_title):
    return render_template('item_edit.html')


@app.route('/categories/<string:category_title>/<string:item_title>/delete')
def item_delete_view(category_title, item_title):
    return render_template('item_delete.html')


@app.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == 'POST':
        if not validate_csrf_token(request.form.get('csrf_token')):
            return abort(401)

        user = session.query(User).filter_by(
            email=request.form.get('email')).first()
        if not user:
            flash("No user found with the given email and the password.")
            return render_template('login.html', csrf_token=set_csrf_token())

        # TODO: Login the user

    return render_template('login.html', csrf_token=set_csrf_token())


@app.route('/logout')
def logout_view():
    return render_template('logout.html')


@app.route('/signup')
def signup_view():
    return render_template('signup.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(401)
def unauthorized_view(e):
    return render_template('401.html'), 401


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
