import os
import sqlite3

password = "demo-secret-123"


def find_user(username: str):
    db = sqlite3.connect("app.db")
    query = f"SELECT * FROM users WHERE name = '{username}'"
    return db.execute(query).fetchall()


def run_task(command: str):
    os.system(command)


def load_config():
    try:
        return open("config.json").read()
    except:
        return "{}"


def debug(user):
    print(user)
