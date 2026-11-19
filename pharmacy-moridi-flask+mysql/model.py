from peewee import (
    Model, MySQLDatabase, IntegerField, CharField,
    DateTimeField, ForeignKeyField
)
from datetime import datetime
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

db = MySQLDatabase(
    DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    charset="utf8mb4",
)


class BaseModel(Model):
    class Meta:
        database = db


class Medicine(BaseModel):
    name  = CharField(max_length=150)
    price = IntegerField()
    stock = IntegerField(default=0)

    class Meta:
        table_name = "medicines"


class Sale(BaseModel):
    medicine = ForeignKeyField(Medicine, backref="sales", on_delete="CASCADE")
    quantity = IntegerField()
    total    = IntegerField()
    sold_at  = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "sales"


def init_db() -> None:
    db.connect(reuse_if_open=True)
    db.create_tables([Medicine, Sale])