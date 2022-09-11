import datetime
from pymongo import MongoClient


MOSCOW_TIMEZONE = datetime.timezone(datetime.timedelta(hours=3))
FORMAT = "%d %b %Y %H:%M:%S %z"

MONGO_DB_HOST = "cleaned"

client = MongoClient(host=MONGO_DB_HOST)
db = client.lousy_vpn_db



def add_user(tg_user_id: int, tg_username: str, ip: str, public_key: str) -> None:
    user = {
        "tg_id": tg_user_id,
        "tg_username": tg_username,
        "allowed_ip": ip,
        "public_key": public_key,
        "get_access_date": datetime.datetime.now(tz=MOSCOW_TIMEZONE).strftime(format=FORMAT)
    }

    db["users"].insert_one(user)