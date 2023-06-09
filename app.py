from flask import Flask, render_template
from recommendations import get_movie

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/<movie>")
def index_get(movie):
    """Homepage GET request"""

    data = get_movie(movie)
    print(type(data))

    return "Found"


if __name__ == '__main__':
    app.run(debug=True)
