from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def hello():
    """Home route rendering the interactive UI."""
    return render_template("index.html")


@app.route("/feature1")
def feature1() -> str:
    """Feature 1 route."""
    return "早上要看股票"


@app.route("/feature2")
def feature2() -> str:
    """Feature 2 route."""
    return "要找下午上班的公司"


if __name__ == "__main__":
    # Start the Flask web application on port 19191
    app.run(port=19191, debug=True)