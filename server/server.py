from flask import Flask
from flask import render_template
app = Flask(__name__, static_url_path='')


@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/callback")
def soundcloud_callback():
    return render_template('/callback.html')

if __name__ == "__main__":
    app.debug = True
    app.run()
