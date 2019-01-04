from flask import Flask
from flask import render_template
from models import Category
from models import Item
from models import session


app = Flask(__name__)


@app.route('/catalog.json')
def catalog_json_view():
    return "rest-api"


@app.route('/')
def dashboard():
    categories = session.query(Category).all()
    items = session.query(Item).order_by('creation_date desc').limit(10).all()

    return render_template('dashboard.html', categories=categories, items=items)


@app.route('/categories/<string:category_title>')
def category_view(category_title):
    return render_template('category.html')


@app.route('/categories/<string:category_title>/<string:item_title>')
def item_view(category_title, item_title):
    return render_template('item.html')


@app.route('/categories/<string:category_title>/<string:item_title>/edit')
def item_edit_view(category_title, item_title):
    return render_template('item_edit.html')


@app.route('/categories/<string:category_title>/<string:item_title>/delete')
def item_delete_view(category_title, item_title):
    return render_template('item_delete.html')


@app.route('/login')
def login_view():
    return render_template('login.html')


@app.route('/logout')
def logout_view():
    return render_template('logout.html')


@app.route('/signup')
def signup_view():
    return render_template('signup.html')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def not_found_view(path):
    return render_template('404.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
