from flask import Flask

app = Flask(__name__)


@app.route('/')
def frontPage():
    return "front-page"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
