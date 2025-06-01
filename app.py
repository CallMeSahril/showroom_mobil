from flask import Flask, render_template
from config import Config
from db import init_db
from routes.mobil_routes import mobil_bp
from routes.dashboard import dashboard_bp

app = Flask(__name__)

init_db(app)
app.register_blueprint(mobil_bp)
app.register_blueprint(dashboard_bp)


@app.route("/")
def home():
    return render_template("layout.html")


app.config.from_object(Config)


if __name__ == '__main__':
    app.run(debug=True)
