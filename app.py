from flask import Flask
from markupsafe import escape


app = Flask(__name__)


@app.route("/<movie>")
def index_get(movie):
    """Homepage GET request"""

    return f"{escape(movie)} you want to match"


app.run(debug=True)
