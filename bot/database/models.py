from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    AutoField,
    IntegerField,
    BooleanField,
)

db = SqliteDatabase("users_base.db")


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = AutoField(primary_key=True)
    user_id = IntegerField(unique=True)  # telegram_id
    username = CharField(null=True)  # username
    first_name = CharField()  # first_name
    second_name = CharField(null=True)  # last_name
    is_sub = BooleanField(default=None, null=True)

    def __str__(self) -> str:
        return "DB ID: {base_id}\nUsername: {username}\nName: {name}\nSurname: {surname}\nTelegram ID: {telegram_id}\nIs Subscriber: {is_sub}".format(
            base_id=self.id,
            username=self.username,
            name=self.first_name,
            surname=self.second_name,
            telegram_id=self.user_id,
            is_sub=self.is_sub,
        )


async def create_tables():
    db.create_tables(BaseModel.__subclasses__())
