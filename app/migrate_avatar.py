from run import app
from app.models import db
from sqlalchemy import inspect, text


with app.app_context():

    columns = [
        column["name"]
        for column in inspect(db.engine).get_columns("users")
    ]

    print("Текущие колонки:", columns)

    if "avatar" not in columns:

        with db.engine.begin() as connection:

            connection.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN avatar VARCHAR(255)"
                )
            )

        print("Поле avatar успешно добавлено.")

    else:

        print("Поле avatar уже существует.")