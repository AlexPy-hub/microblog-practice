from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import User, db


auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Заполните все поля.")
            return render_template("register.html")

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Пользователь с таким именем или email уже существует.")
            return render_template("register.html")

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
        )

        db.session.add(user)
        db.session.commit()

        flash("Регистрация прошла успешно!")
        return redirect(url_for("index"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter(
            (User.username == login) | (User.email == login.lower())
        ).first()

        if user is None or not check_password_hash(
            user.password_hash,
            password
        ):
            flash("Неверное имя пользователя, email или пароль.")
            return render_template("login.html")

        session["user_id"] = user.id
        session["username"] = user.username

        flash(f"Вы вошли как {user.username}.")

        return redirect(url_for("index"))

    return render_template("login.html")


@auth.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)

    flash("Вы вышли из аккаунта.")

    return redirect(url_for("index"))