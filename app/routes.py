from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from pathlib import Path
from uuid import uuid4

from app.models import Comment, Like, Message, Post, User, db


main = Blueprint("main", __name__)


# =========================
# ПОСТЫ
# =========================

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

    post = db.session.get(Post, post_id)

    if post is None:
        flash("Публикация не найдена.")
        return redirect(url_for("index"))

    if post.user_id != session["user_id"]:
        flash(
            "Вы можете редактировать только свои публикации."
        )

        return redirect(url_for("index"))

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:

            flash(
                "Заполните заголовок и текст публикации."
            )

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

    post = db.session.get(Post, post_id)

    if post is None:
        flash("Публикация не найдена.")
        return redirect(url_for("index"))

    if post.user_id != session["user_id"]:
        flash(
            "Вы можете удалить только свои публикации."
        )

        return redirect(url_for("index"))

    # Сначала удаляем все лайки этого поста.
    # Это необходимо, потому что likes.post_id
    # является обязательным полем (NOT NULL).
    Like.query.filter_by(
        post_id=post.id
    ).delete(
        synchronize_session=False
    )

    # После удаления лайков удаляем сам пост.
    db.session.delete(post)
    db.session.commit()

    flash("Публикация удалена.")

    return redirect(url_for("index"))


# =========================
# ЛАЙКИ
# =========================

@main.route(
    "/posts/<int:post_id>/like",
    methods=["POST"]
)
def toggle_like(post_id):

    if "user_id" not in session:
        return jsonify({
            "error": "Необходимо войти в аккаунт."
        }), 401

    post = db.session.get(Post, post_id)

    if post is None:
        return jsonify({
            "error": "Публикация не найдена."
        }), 404

    existing_like = Like.query.filter_by(
        user_id=session["user_id"],
        post_id=post.id
    ).first()

    if existing_like:

        db.session.delete(existing_like)

        liked = False

    else:

        like = Like(
            user_id=session["user_id"],
            post_id=post.id
        )

        db.session.add(like)

        liked = True

    db.session.commit()

    likes_count = Like.query.filter_by(
        post_id=post.id
    ).count()

    return jsonify({
        "liked": liked,
        "likes_count": likes_count
    })


# =========================
# КОММЕНТАРИИ
# =========================

@main.route(
    "/posts/<int:post_id>/comment",
    methods=["POST"]
)
def add_comment(post_id):

    if "user_id" not in session:
        flash("Сначала войдите в аккаунт.")
        return redirect(url_for("auth.login"))

    post = db.session.get(Post, post_id)

    if post is None:
        flash("Публикация не найдена.")
        return redirect(url_for("index"))

    content = request.form.get(
        "content",
        ""
    ).strip()

    if not content:

        flash(
            "Комментарий не может быть пустым."
        )

        return redirect(
            url_for("index")
        )

    comment = Comment(
        content=content,
        user_id=session["user_id"],
        post_id=post.id,
    )

    db.session.add(comment)
    db.session.commit()

    flash("Комментарий добавлен.")

    return redirect(
        url_for("index")
    )


@main.route(
    "/comments/<int:comment_id>/delete",
    methods=["POST"]
)
def delete_comment(comment_id):

    if "user_id" not in session:
        flash("Сначала войдите в аккаунт.")
        return redirect(url_for("auth.login"))

    comment = db.session.get(
        Comment,
        comment_id
    )

    if comment is None:
        flash("Комментарий не найден.")
        return redirect(url_for("index"))

    if comment.user_id != session["user_id"]:

        flash(
            "Вы можете удалить только свои комментарии."
        )

        return redirect(
            url_for("index")
        )

    db.session.delete(comment)
    db.session.commit()

    flash("Комментарий удалён.")

    return redirect(
        url_for("index")
    )


# =========================
# ЛИЧНЫЕ СООБЩЕНИЯ
# =========================

@main.route("/messages")
def messages_list():

    if "user_id" not in session:
        flash("Сначала войдите в аккаунт.")
        return redirect(url_for("auth.login"))

    current_user = db.session.get(
        User,
        session["user_id"]
    )

    if current_user is None:
        session.pop("user_id", None)

        flash("Пользователь не найден.")

        return redirect(
            url_for("auth.login")
        )

    sent_to = db.session.query(
        Message.recipient_id
    ).filter(
        Message.sender_id == current_user.id
    ).all()

    received_from = db.session.query(
        Message.sender_id
    ).filter(
        Message.recipient_id == current_user.id
    ).all()

    sent_ids = [
        row[0]
        for row in sent_to
    ]

    received_ids = [
        row[0]
        for row in received_from
    ]

    user_ids = set(
        sent_ids + received_ids
    )

    users = []

    if user_ids:

        users = User.query.filter(
            User.id.in_(user_ids)
        ).all()

    conversations = []

    for user in users:

        last_message = Message.query.filter(
            (
                (Message.sender_id == current_user.id)
                & (
                    Message.recipient_id == user.id
                )
            )
            |
            (
                (Message.sender_id == user.id)
                & (
                    Message.recipient_id == current_user.id
                )
            )
        ).order_by(
            Message.created_at.desc()
        ).first()

        unread_count = Message.query.filter_by(
            sender_id=user.id,
            recipient_id=current_user.id,
            is_read=False
        ).count()

        if last_message:

            conversations.append({
                "user": user,
                "last_message": last_message,
                "unread_count": unread_count,
            })

    conversations.sort(
        key=lambda item: item["last_message"].created_at,
        reverse=True
    )

    return render_template(
        "messages_list.html",
        conversations=conversations,
    )


# =========================
# ПЕРЕПИСКА
# =========================

@main.route(
    "/messages/<username>",
    methods=["GET", "POST"]
)
def messages(username):

    if "user_id" not in session:
        flash("Сначала войдите в аккаунт.")
        return redirect(url_for("auth.login"))

    current_user = db.session.get(
        User,
        session["user_id"]
    )

    if current_user is None:
        session.pop("user_id", None)

        flash("Пользователь не найден.")

        return redirect(
            url_for("auth.login")
        )

    recipient = User.query.filter_by(
        username=username
    ).first_or_404()

    if recipient.id == current_user.id:

        flash(
            "Нельзя отправить сообщение самому себе."
        )

        return redirect(
            url_for(
                "main.profile",
                username=recipient.username
            )
        )

    # =========================
    # ОТПРАВКА СООБЩЕНИЯ
    # =========================

    if request.method == "POST":

        content = request.form.get(
            "content",
            ""
        ).strip()

        if not content:

            if request.headers.get(
                "X-Requested-With"
            ) == "XMLHttpRequest":

                return jsonify({
                    "error": (
                        "Сообщение не может быть пустым."
                    )
                }), 400

            flash(
                "Сообщение не может быть пустым."
            )

            return redirect(
                url_for(
                    "main.messages",
                    username=recipient.username
                )
            )

        message = Message(
            content=content,
            sender_id=current_user.id,
            recipient_id=recipient.id,
            is_read=False,
        )

        db.session.add(message)
        db.session.commit()
        db.session.refresh(message)

        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest":

            return jsonify({
                "success": True,
                "content": message.content,
                "created_at": (
                    message.created_at.strftime("%H:%M")
                ),
                "message_id": message.id,
            }), 200

        return redirect(
            url_for(
                "main.messages",
                username=recipient.username
            )
        )

    # =========================
    # ЗАГРУЗКА ПЕРЕПИСКИ
    # =========================

    conversation = Message.query.filter(
        (
            (Message.sender_id == current_user.id)
            & (
                Message.recipient_id == recipient.id
            )
        )
        |
        (
            (Message.sender_id == recipient.id)
            & (
                Message.recipient_id == current_user.id
            )
        )
    ).order_by(
        Message.created_at.asc(),
        Message.id.asc()
    ).all()

    unread_messages_changed = False

    for message in conversation:

        if (
            message.recipient_id == current_user.id
            and not message.is_read
        ):

            message.is_read = True

            unread_messages_changed = True

    if unread_messages_changed:
        db.session.commit()

    return render_template(
        "messages.html",
        recipient=recipient,
        conversation=conversation,
    )


# =========================
# УДАЛЕНИЕ СООБЩЕНИЯ
# =========================

@main.route(
    "/messages/delete/<int:message_id>",
    methods=["POST"]
)
def delete_message(message_id):

    if "user_id" not in session:
        return jsonify({
            "error": "Необходимо войти в аккаунт."
        }), 401

    current_user = db.session.get(
        User,
        session["user_id"]
    )

    if current_user is None:
        return jsonify({
            "error": "Пользователь не найден."
        }), 401

    message = db.session.get(
        Message,
        message_id
    )

    if message is None:
        return jsonify({
            "error": "Сообщение не найдено."
        }), 404

    if message.sender_id != current_user.id:
        return jsonify({
            "error": (
                "Вы можете удалить только свои сообщения."
            )
        }), 403

    db.session.delete(message)
    db.session.commit()

    return jsonify({
        "success": True,
        "message_id": message_id,
    }), 200


# =========================
# НОВЫЕ СООБЩЕНИЯ
# =========================

@main.route(
    "/messages/<username>/new",
    methods=["GET"]
)
def get_new_messages(username):

    if "user_id" not in session:
        return jsonify({
            "error": "Необходимо войти в аккаунт."
        }), 401

    current_user = db.session.get(
        User,
        session["user_id"]
    )

    if current_user is None:
        return jsonify({
            "error": "Пользователь не найден."
        }), 401

    recipient = User.query.filter_by(
        username=username
    ).first_or_404()

    try:

        last_message_id = int(
            request.args.get(
                "after",
                0
            )
        )

    except (TypeError, ValueError):

        last_message_id = 0

    if last_message_id < 0:
        last_message_id = 0

    new_messages = Message.query.filter(
        Message.id > last_message_id,
        Message.sender_id == recipient.id,
        Message.recipient_id == current_user.id
    ).order_by(
        Message.id.asc()
    ).all()

    messages_data = []

    unread_messages_changed = False

    for message in new_messages:

        if not message.is_read:

            message.is_read = True

            unread_messages_changed = True

        messages_data.append({
            "id": message.id,
            "content": message.content,
            "created_at": (
                message.created_at.strftime("%H:%M")
            ),
        })

    if unread_messages_changed:
        db.session.commit()

    return jsonify({
        "success": True,
        "messages": messages_data,
    })


# =========================
# ПРОФИЛЬ
# =========================

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


# =========================
# РЕДАКТИРОВАНИЕ ПРОФИЛЯ
# =========================

@main.route(
    "/profile/edit",
    methods=["GET", "POST"]
)
def edit_profile():

    if "user_id" not in session:

        flash(
            "Сначала войдите в аккаунт."
        )

        return redirect(
            url_for("auth.login")
        )

    user = db.session.get(
        User,
        session["user_id"]
    )

    if user is None:

        session.pop("user_id", None)

        flash(
            "Пользователь не найден."
        )

        return redirect(
            url_for("auth.login")
        )

    if request.method == "POST":

        avatar_file = request.files.get(
            "avatar"
        )

        if (
            not avatar_file
            or not avatar_file.filename
        ):

            flash(
                "Выберите изображение."
            )

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

                try:
                    old_file.unlink()
                except OSError:
                    pass

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