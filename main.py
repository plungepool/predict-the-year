from flask import Flask

app = Flask(__name__)


# Ties a page on your website to a function
# @ signifies a decorator - way to wrap a function and modify its behavior
@app.route('/')
def index():
    return 'This is the homepage'


if __name__ == "__main__":
    app.run(debug=True)
