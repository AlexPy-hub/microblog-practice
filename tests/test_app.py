import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import User, Post, db


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key",
    })

    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("test-password"),
        )

        db.session.add(user)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client):
    return client.post(
        "/login",
        data={
            "login": "testuser",
            "password": "test-password",
        },
        follow_redirects=True,
    )


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Microblog" in response.data


def test_register(client, app):
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(
            username="newuser"
        ).first()

        assert user is not None
        assert user.email == "new@example.com"


def test_login(client):
    response = client.post(
        "/login",
        data={
            "login": "testuser",
            "password": "test-password",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert session.get("user_id") is not None
        assert session.get("username") == "testuser"


def test_create_post(client, app):
    login(client)

    response = client.post(
        "/posts/create",
        data={
            "title": "Test post",
            "content": "Test content",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        post = Post.query.filter_by(
            title="Test post"
        ).first()

        assert post is not None
        assert post.content == "Test content"


def test_edit_post(client, app):
    login(client)

    with app.app_context():
        user = User.query.filter_by(
            username="testuser"
        ).first()

        post = Post(
            title="Old title",
            content="Old content",
            user_id=user.id,
        )

        db.session.add(post)
        db.session.commit()

        post_id = post.id

    response = client.post(
        f"/posts/{post_id}/edit",
        data={
            "title": "New title",
            "content": "New content",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        post = db.session.get(Post, post_id)

        assert post is not None
        assert post.title == "New title"
        assert post.content == "New content"


def test_delete_post(client, app):
    login(client)

    with app.app_context():
        user = User.query.filter_by(
            username="testuser"
        ).first()

        post = Post(
            title="Delete me",
            content="This post will be deleted",
            user_id=user.id,
        )

        db.session.add(post)
        db.session.commit()

        post_id = post.id

    response = client.post(
        f"/posts/{post_id}/delete",
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        post = db.session.get(Post, post_id)

        assert post is None


def test_api_get_posts(client, app):
    with app.app_context():
        user = User.query.filter_by(
            username="testuser"
        ).first()

        post = Post(
            title="API test",
            content="API content",
            user_id=user.id,
        )

        db.session.add(post)
        db.session.commit()

    response = client.get("/api/posts")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "API test"


def test_api_create_post(client):
    response = client.post(
        "/api/posts",
        json={
            "title": "API created",
            "content": "Created through API",
            "user_id": 1,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Post created successfully"
    assert data["post"]["title"] == "API created"


def test_api_get_post(client, app):
    with app.app_context():
        user = User.query.filter_by(
            username="testuser"
        ).first()

        post = Post(
            title="Single post",
            content="Single content",
            user_id=user.id,
        )

        db.session.add(post)
        db.session.commit()

        post_id = post.id

    response = client.get(
        f"/api/posts/{post_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == post_id
    assert data["title"] == "Single post"


def test_api_update_post(client, app):
    with app.app_context():
        user = User.query.filter_by(
            username="testuser"
        ).first()

        post = Post(
            title="Old API title",
            content="Old API content",
            user_id=user.id,
        )

        db.session.add(post)
        db.session.commit()

        post_id = post.id

    response = client.put(
        f"/api/posts/{post_id}",
        json={
            "title": "Updated API title",
            "content": "Updated API content",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Post updated successfully"
    assert data["post"]["title"] == "Updated API title"


def test_api_delete_post(client, app):
    with app.app_context():
        user = User.query.filter_by(
            username="testuser"
        ).first()

        post = Post(
            title="API delete",
            content="Delete through API",
            user_id=user.id,
        )

        db.session.add(post)
        db.session.commit()

        post_id = post.id

    response = client.delete(
        f"/api/posts/{post_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Post deleted successfully"

    response = client.get(
        f"/api/posts/{post_id}"
    )

    assert response.status_code == 404