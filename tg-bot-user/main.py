import os
import keyboard
import strings
import database
import wireguard
from config import BOT_TOKEN
from telegram import Update, ParseMode, InputMediaPhoto, Message
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Filters

ADMIN_LIST = ["cleaned", "cleaned"]


def start(update: Update, context: CallbackContext) -> None:
    first_name = update.effective_user.first_name
    update.message.reply_text(strings.START_MSG.format(first_name), 
                              parse_mode=ParseMode.HTML, 
                              reply_markup=keyboard.START_KEYBOARD)


def get_access(update: Update, context: CallbackContext) -> None:
    tg_id = update.effective_user.id
    tg_username= update.effective_user.username
    
    peer = wireguard.create_peer(tg_id)
    
    if peer is None:
        print("All ips are taken")
        update.message.reply_text("Unexpected error, try again later.")
        return
    
    
    #TODO:update traffic values for all users in db
    
    wireguard.restart_wireguard()

    database.add_user(tg_id, tg_username, peer.allowed_ip, peer.public_key)
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(f'/etc/wireguard/peers/{tg_id}/qr.png', 'rb'), caption=strings.GUIDE)
    context.bot.send_document(chat_id=update.effective_chat.id, document=open(f'/etc/wireguard/peers/{tg_id}/{tg_id}.conf', 'rb'))

    #database.add_user(tg_id, tg_username, peer.allowed_ip, "asfsj)
    #context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(f'/etc/wireguard/peers/ponomarev_mobile/qr.png', 'rb'), caption=strings.GUIDE)
    #context.bot.send_document(chat_id=update.effective_chat.id, document=open(f'/etc/wireguard/peers/ponomarev/pc/kp_pc.conf', 'rb'))


def get_count_connected(update: Update, context: CallbackContext) -> None:
    connected_count = wireguard.count_connected()
    update.message.reply_text(str(connected_count))


def main() -> None:
    updater = Updater(token=BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start, run_async=True))
    dp.add_handler(CommandHandler('count_connected', get_count_connected, run_async=True, filters=Filters.user(username=ADMIN_LIST)))

    dp.add_handler(CallbackQueryHandler(get_access, pattern=r"get_access", run_async=True))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
