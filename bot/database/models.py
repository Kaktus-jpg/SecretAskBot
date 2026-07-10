from datetime import datetime

from peewee import (
    AutoField,
    BigIntegerField,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
)

from bot.utils import utcnow

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
    is_sub = BooleanField(default=False)

    def __str__(self) -> str:
        return "DB ID: {base_id}\nUsername: {username}\nName: {name}\nSurname: {surname}\nTelegram ID: {telegram_id}\nIs Subscriber: {is_sub}".format(
            base_id=self.id,
            username=self.username,
            name=self.first_name,
            surname=self.second_name,
            telegram_id=self.user_id,
            is_sub=self.is_sub,
        )


class AnonymousMessage(BaseModel):
    id = AutoField()

    # Кто написал исходное анонимное сообщение.
    sender = ForeignKeyField(
        User,
        column_name="sender_id",
        backref="sent_anonymous_messages",
        on_delete="CASCADE",
    )

    # Кто это сообщение получил.
    receiver = ForeignKeyField(
        User,
        column_name="receiver_id",
        backref="received_anonymous_messages",
        on_delete="CASCADE",
    )

    # Telegram message_id сообщения, которое бот доставил получателю.
    receiver_message_id = IntegerField(null=True)

    # Можно ли ещё отвечать на это исходное сообщение.
    is_active = BooleanField(default=True)

    created_at = DateTimeField(default=datetime.now)
    replied_at = DateTimeField(null=True)

    class Meta:
        table_name = "anonymous_messages"
        indexes = ((("receiver", "is_active"), False),)


class Payment(BaseModel):
    user = ForeignKeyField(User, backref="payments", on_delete="CASCADE")

    telegram_payment_charge_id = CharField(unique=True)
    invoice_payload = CharField()

    amount_xtr = BigIntegerField()
    paid_at = DateTimeField(default=utcnow())

    refund_until = DateTimeField(index=True)
    refunded_at = DateTimeField(null=True)

    status = CharField(default="paid")  # paid / refunding / refunded


async def create_tables():
    db.create_tables(BaseModel.__subclasses__())
