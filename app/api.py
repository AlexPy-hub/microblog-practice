from flask import Blueprint, jsonify, request

from app.models import Post, User, db


api = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


@api.route("/posts", methods=["GET"])
def get_posts():

    posts = Post.query.order_by(
        Post.created_at.desc()
    ).all()

    return jsonify([
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at.isoformat(),
            "updated_at": (
                post.updated_at.isoformat()
                if post.updated_at
                else None
            ),
            "user_id": post.user_id,
            "username": post.author.username,
        }
        for post in posts
    ])


@api.route("/posts", methods=["POST"])
def create_post_api():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON body is required"
        }), 400

    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    user_id = data.get("user_id")

    if not title or not content or not user_id:
        return jsonify({
            "error": "title, content and user_id are required"
        }), 400

    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({
            "error": "User not found"
        }), 404

    post = Post(
        title=title,
        content=content,
        user_id=user_id
    )

    db.session.add(post)
    db.session.commit()

    return jsonify({
        "message": "Post created successfully",
        "post": {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at.isoformat(),
            "updated_at": (
                post.updated_at.isoformat()
                if post.updated_at
                else None
            ),
            "user_id": post.user_id,
            "username": user.username
        }
    }), 201


@api.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):

    post = db.session.get(Post, post_id)

    if post is None:
        return jsonify({
            "error": "Post not found"
        }), 404

    return jsonify({
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at.isoformat(),
        "updated_at": (
            post.updated_at.isoformat()
            if post.updated_at
            else None
        ),
        "user_id": post.user_id,
        "username": post.author.username,
    })


@api.route("/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):

    post = db.session.get(Post, post_id)

    if post is None:
        return jsonify({
            "error": "Post not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON body is required"
        }), 400

    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    if not title or not content:
        return jsonify({
            "error": "title and content are required"
        }), 400

    post.title = title
    post.content = content

    db.session.commit()

    return jsonify({
        "message": "Post updated successfully",
        "post": {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at.isoformat(),
            "updated_at": (
                post.updated_at.isoformat()
                if post.updated_at
                else None
            ),
            "user_id": post.user_id,
            "username": post.author.username,
        }
    })


@api.route("/posts/<int:post_id>", methods=["DELETE"])
def delete_post_api(post_id):

    post = db.session.get(Post, post_id)

    if post is None:
        return jsonify({
            "error": "Post not found"
        }), 404

    db.session.delete(post)
    db.session.commit()

    return jsonify({
        "message": "Post deleted successfully"
    })