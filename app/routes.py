from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from pathlib import Path
from uuid import uuid4

from app.models import Post, User, db


main = Blueprint("main", __name__)


@main.route("/posts/create", methods=["GET", "POST"])
def create_post():

    if "user_id" not in session:
        flash("Сначала войдите в аккаунт.")
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Заполните заголовок и текст публикации.")

            return render_template(
                "create_post.html"
            )

        post = Post(
            title=title,
            content=content,
            user_id=session["user_id"],
        )

        db.session.add(post)
        db.session.commit()

        flash("Публикация создана!")

        return redirect(url_for("index"))

    return render_template(
        "create_post.html"
    )


@main.route(
    "/posts/<int:post_id>/edit",
    methods=["GET", "POST"]
)
def edit_post(post_id):

    if "user_id" not in session:
        flash("Сначала войдите в аккаунт.")
        return redirect(url_for("auth.login"))

    post = Post.query.get_or_404(post_id)

    if post.user_id != session["user_id"]:
        flash("Вы можете редактировать только свои публикации.")

        return redirect(url_for("index"))

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:

            flash("Заполните заголовок и текст публикации.")

            return render_template(
                "edit_post.html",
                post=post
            )

        post.title = title
        post.content = content

        db.session.commit()

        flash("Публикация обновлена!")

        return redirect(url_for("index"))

    return render_template(
        "edit_post.html",
        post=post
    )


@main.route(
    "/posts/<int:post_id>/delete",
    methods=["POST"]
)
def delete_post(post_id):

    if "user_id" not in session:
        flash("Сначала войдите в аккаунт.")
        return redirect(url_for("auth.login"))

    post = Post.query.get_or_404(post_id)

    if post.user_id != session["user_id"]:
        flash("Вы можете удалить только свои публикации.")

        return redirect(url_for("index"))

    db.session.delete(post)

    db.session.commit()

    flash("Публикация удалена.")

    return redirect(url_for("index"))


@main.route("/profile/<username>")
def profile(username):

    user = User.query.filter_by(
        username=username
    ).first_or_404()

    posts = Post.query.filter_by(
        user_id=user.id
    ).order_by(
        Post.created_at.desc()
    ).all()

    return render_template(
        "profile.html",
        user=user,
        posts=posts
    )


@main.route(
    "/profile/edit",
    methods=["GET", "POST"]
)
def edit_profile():

    if "user_id" not in session:
        flash("Сначала войдите в аккаунт.")

        return redirect(
            url_for("auth.login")
        )

    user = db.session.get(
        User,
        session["user_id"]
    )

    if user is None:
        flash("Пользователь не найден.")

        return redirect(
            url_for("index")
        )

    if request.method == "POST":

        avatar_file = request.files.get(
            "avatar"
        )

        if (
            not avatar_file
            or not avatar_file.filename
        ):

            flash("Выберите изображение.")

            return render_template(
                "edit_profile.html",
                user=user
            )

        extension = Path(
            avatar_file.filename
        ).suffix.lower()

        allowed_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
        }

        if extension not in allowed_extensions:

            flash(
                "Разрешены только PNG, JPG, JPEG, GIF и WEBP."
            )

            return render_template(
                "edit_profile.html",
                user=user
            )

        upload_folder = (
            Path(current_app.static_folder)
            / "uploads"
            / "avatars"
        )

        upload_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        filename = (
            f"{uuid4().hex}{extension}"
        )

        avatar_file.save(
            upload_folder / filename
        )

        old_avatar = user.avatar

        user.avatar = filename

        db.session.commit()

        if old_avatar:

            old_file = (
                upload_folder / old_avatar
            )

            if old_file.exists():
                old_file.unlink()

        flash(
            "Аватар успешно обновлён."
        )

        return redirect(
            url_for(
                "main.profile",
                username=user.username
            )
        )

    return render_template(
        "edit_profile.html",
        user=user
    )