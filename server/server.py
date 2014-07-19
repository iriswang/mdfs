from flask import Flask
app = Flask(__name__, static_url_path='')


@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.debug = True
    app.run()
