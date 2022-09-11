import telegram

START_KEYBOARD = telegram.InlineKeyboardMarkup(
    [
        [
            telegram.InlineKeyboardButton('Поддержка в ВК', "https://www.vk.com/"),
            telegram.InlineKeyboardButton('Получить доступ', callback_data='get_access'),
        ]
    ]
)