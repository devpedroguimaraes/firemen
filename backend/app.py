from pathlib import Path

from flask import Flask, send_from_directory


BASE_DIR = Path(__file__).resolve().parent.parent

PUBLIC_DIR = BASE_DIR / "frontend" / "public"
CSS_DIR = BASE_DIR / "frontend" / "css"
JS_DIR = BASE_DIR / "frontend" / "js"


app = Flask(__name__)


@app.route("/")
def home():
    return send_from_directory(PUBLIC_DIR, "index.html")


@app.route("/css/<path:filename>")
def css(filename):
    return send_from_directory(CSS_DIR, filename)


@app.route("/js/<path:filename>")
def js(filename):
    return send_from_directory(JS_DIR, filename)


@app.route("/<path:filename>")
def frontend(filename):
    return send_from_directory(PUBLIC_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True)