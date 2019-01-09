from authentication.auth import Authentication
from authentication.google import AccessTokenValidationError
from flask import abort
from flask import flash
from flask import Flask
from flask import g
from flask import jsonify
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import session as flask_session
from flask import url_for
from models import Category
from models import Item
from oauth2client.client import FlowExchangeError
import json
import random
import string


app = Flask(__name__)
auth = Authentication()

app.jinja_env.globals.update(
    is_authenticated=lambda: auth.is_authenticated())


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


@app.before_request
def restore_login_session():
    auth.restore_session(flask_session.get('access_token'))


@app.route('/catalog.json')
def catalog_json_view():
    categories = Category.query().all()

    return jsonify(
        {'categories': [category.as_dict() for category in categories]})

CLIENT_ID = json.loads(
    open('google_secrets.json', 'r').read())['web']['client_id']


@app.route('/googlelogin', methods=['POST'])
def googlelogin():
    # Validate state token
    if not validate_csrf_token(request.form.get('csrf_token')):
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    try:
        auth.login('google', request.form.get('id_token'))
    except (AccessTokenValidationError, FlowExchangeError, ValueError) as err:
        response = make_response(json.dumps(err.message), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    return 'successful'


@app.route('/')
def dashboard():
    categories = Category.query().all()
    items = Item.query().order_by('creation_date desc').limit(10).all()

    return render_template('dashboard.html', categories=categories, items=items)


@app.route('/categories/<string:category_title>')
def category_view(category_title):
    categories_query = Category.query()
    categories = categories_query.all()
    category = categories_query.filter_by(title=category_title).first()

    if not category:
        return abort(404)
    return render_template('category.html',
                           categories=categories, category=category)


@app.route('/categories/<string:category_title>/<string:item_title>')
def item_view(category_title, item_title):
    item = Item.query().filter_by(title=item_title).first()
    if not item:
        return abort(404)
    return render_template('item.html', item=item)


@app.route('/categories/<string:category_title>/<string:item_title>/edit')
def item_edit_view(category_title, item_title):
    return render_template('item_edit.html')


@app.route('/categories/<string:category_title>/<string:item_title>/delete')
def item_delete_view(category_title, item_title):
    return render_template('item_delete.html')


@app.route('/login', methods=['GET'])
def login_view():
    if auth.is_authenticated():
        flash("You are already logged in")
        return redirect(url_for('dashboard'))
    return render_template('login.html',
                           csrf_token=set_csrf_token(),
                           googleclientid=CLIENT_ID)


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
