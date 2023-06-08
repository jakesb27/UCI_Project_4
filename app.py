
from markupsafe import escape
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('static/index.html')

@app.route("/<movie>")
def index_get(movie):
    """Homepage GET request"""

    return f"{escape(movie)} you want to match"

if __name__ == '__main__':
    app.run(debug=True)
