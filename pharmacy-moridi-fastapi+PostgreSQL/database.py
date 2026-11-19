from peewee import PostgresqlDatabase
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

db = PostgresqlDatabase(
    DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
)


def init_db() -> None:
    db.connect(reuse_if_open=True)
    from models import Medicine, Sale
    db.create_tables([Medicine, Sale])