import os
from dotenv import load_dotenv
import psycopg2
from werkzeug.security import generate_password_hash

load_dotenv(dotenv_path="../.env")


def create_database_tables():
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            port=os.getenv("DATABASE_PORT")
        )

        cursor = connection.cursor()
        with open("schema.sql", "r") as f:
            cursor.execute(f.read())

        hashed_pw = generate_password_hash("root")
        cursor.execute(
            "INSERT INTO users (username, password, user_role) VALUES (%s, %s, %s)",
            ("root", hashed_pw, "admin"))

        connection.commit()

    except psycopg2.Error as e:
        print(f"psycopg2.Error: {e}")

    except Exception as e:
        print(f"Exception: {e}")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    print("Creating tables")
    create_database_tables()
    print("Tables created")
