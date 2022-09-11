import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters
from config import BOT_TOKEN


USERS = ["ponamber", "kiruxaspb"]


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("vpn admin bot")


def add_user(update: Update, context: CallbackContext) -> None:
    username = context.args[0]


def delete_user(update: Update, context: CallbackContext) -> None:
    pass


def get_stat(update: Update, context: CallbackContext) -> None:
    with open('/etc/wireguard/info.txt', 'r') as file:
        stats = file.readlines()

    with open('/etc/wireguard/wg0.conf', 'r') as file:
        config = file.readlines()

        names = []
    for line in config:
        if line.startswith("#"):
            names.append(line)
    
    update.message.reply_text(str(names))


def main() -> None:
    updater = Updater(token=BOT_TOKEN)
    dp = updater.dispatcher 
    dp.add_handler(CommandHandler('start', start, run_async=True, filters=Filters.user(username=USERS)))
    dp.add_handler(CommandHandler('get_stat', get_stat, run_async=True, filters=Filters.user(username=USERS)))
    dp.add_handler(CommandHandler('add_user', add_user, run_async=True, filters=Filters.user(username=USERS)))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

