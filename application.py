from authentication.auth import Authentication
from authentication.google import AccessTokenValidationError
from flask import abort
from flask import flash
from flask import Flask
from flask import jsonify
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import session as flask_session
from flask import url_for
from markupsafe import escape
from models import Category
from models import Item
from models import Session
from oauth2client.client import FlowExchangeError
from security.csrf import csrf_protection
from security.routes import requires_auth
import json


app = Flask(__name__)
auth = Authentication()

app.jinja_env.globals.update(
    is_authenticated=lambda: auth.is_authenticated())


@app.context_processor
def inject_user():
    return dict(user=auth.get_current_user())


@app.before_request
def restore_login_session():
    auth.restore_session()


@app.route('/catalog.json')
def catalog_json_view():
    categories = Category.query().all()

    return jsonify(
        {'categories': [category.as_dict() for category in categories]})

CLIENT_ID = json.loads(
    open('google_secrets.json', 'r').read())['web']['client_id']


@app.route('/googlelogin', methods=['POST'])
@csrf_protection
def googlelogin():
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

    if not category_title == item.category.title:
        return abort(404)

    return render_template('item.html', item=item)


@app.route('/categories/item/add', methods=['GET', 'POST'])
@requires_auth
def item_add_view():
    def render():
        return render_template(
            'item_add.html',
            categories=categories,
            category_id=int(request.args.get('category_id', 0)))

    categories = Category.query().all()

    if request.method == 'POST':
        category_id = escape(request.form.get('category_id'))
        category = Category.query().get(category_id)

        if not category:
            flash("No category fouond with ID {}".format(category_id))
            return render()

        Item.create(
            title=escape(request.form.get('title')),
            description=escape(request.form.get('description')),
            category=category,
            )
        flash("Successfully added Item")
        return redirect(url_for('dashboard'))
    return render()


@app.route('/categories/<string:category_title>/<string:item_title>/edit', methods=['GET', 'POST'])
@requires_auth
def item_edit_view(category_title, item_title):
    def render():
        return render_template('item_edit.html', categories=categories, item=item)

    categories = Category.query().all()
    item = Item.query().filter_by(title=item_title).first()

    if not item:
        return abort(404)

    if not category_title == item.category.title:
        return abort(404)

    if request.method == 'POST':
        category_id = escape(request.form.get('category_id'))
        category = Category.query().get(category_id)

        if not category:
            flash("No category fouond with ID {}".format(category_id))
            return render()

        item.title = escape(request.form.get('title'))
        item.description = escape(request.form.get('description'))
        item.category = category
        Session.commit()
        flash("Successfully updated Item")
        return redirect(url_for(
            'item_view', category_title=category.title, item_title=item.title))
    return render()


@app.route('/categories/<string:category_title>/<string:item_title>/delete',
           methods=['GET', 'POST'])
@requires_auth
def item_delete_view(category_title, item_title):
    item = Item.query().filter_by(title=item_title).first()

    if not item:
        return abort(404)

    if not category_title == item.category.title:
        return abort(404)

    if request.method == 'POST':
        item.delete()
        flash("Item successfully deleted")
        return redirect(url_for('dashboard'))
    return render_template('item_delete.html', item=item)


@app.route('/login', methods=['GET'])
@csrf_protection
def login_view():
    if auth.is_authenticated():
        flash("You are already logged in")
        return redirect(url_for('dashboard'))
    return render_template('login.html',
                           csrf_token=flask_session.get('csrf_token'),
                           googleclientid=CLIENT_ID)


@app.route('/logout')
@requires_auth
def logout_view():
    auth.logout()
    flash("You have been logged out successfully")
    return redirect(url_for('dashboard'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(401)
def unauthorized_view(e):
    return redirect(url_for('login_view'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
