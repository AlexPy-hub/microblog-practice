from flask import Flask, render_template, session

from config import Config
from app.models import Post, User, db
from app.auth import auth
from app.routes import main
from app.api import api


def create_app(test_config=None):

    app = Flask(__name__)

    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(api)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():

        posts = Post.query.order_by(
            Post.created_at.desc()
        ).all()

        return render_template(
            "index.html",
            posts=posts
        )

    @app.context_processor
    def inject_current_user():

        current_user = None

        if session.get("user_id"):

            current_user = db.session.get(
                User,
                session["user_id"]
            )

        return {
            "current_user": current_user
        }

    return app