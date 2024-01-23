from typing import Self
import telebot # сама библиотека telebot
import time # необходим для cрока /mute и автоматического размута после срока мута
from datetime import datetime, timedelta


bot = telebot.TeleBot('6220392068:AAG8ZWdj3enYvufE9sKUZXkspHupHr5CfpU') # в TOKEN мы вводим непосредственно сам полученный токен.

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я Чат-Менеджер COSPAY")

@bot.message_handler(commands=['kick'])
def kick_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно кикнуть администратора.")
        else:
            bot.kick_chat_member(chat_id, user_id)
            bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} был кикнут.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите кикнуть.")

@bot.message_handler(commands=['mute'])
def mute_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status == 'administrator' or user_status == 'creator' or user_status == 'moderator':
            bot.reply_to(message, "Невозможно замутить администратора.")
        else:
            duration = 60 # Значение по умолчанию - 1 минута
            args = message.text.split()[1:]
            if args:
                try:
                    duration = int(args[0])
                except ValueError:
                    bot.reply_to(message, "Неправильный формат времени.")
                    return
                if duration < 1:
                    bot.reply_to(message, "Время должно быть положительным числом.")
                    return
                if duration > 20160:
                    bot.reply_to(message, "Максимальное время - 14 деней.")
                    return
            bot.restrict_chat_member(chat_id, user_id, until_date=time.time()+duration*60)
            bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} замучен на {duration} минут.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите замутить.")

@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} размучен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите размутить.")

# Функция для проверки, является ли пользователь администратором чата
def is_admin(message: telebot.types.Message) -> bool:
    chat_id = message.chat.id
    user_id = message.from_user.id
    # Получаем список администраторов чата
    admins = bot.get_chat_administrators(chat_id)
    # Проверяем, есть ли пользователь среди них
    for admin in admins:
        if admin.user.id == user_id:
            return True
    return False

# Функция для бана пользователя на определенное время
def ban_user(message: telebot.types.Message, user_id: int, duration: int) -> None:
    chat_id = message.chat.id
    # Баним пользователя
    bot.kick_chat_member(chat_id, user_id, until_date=time.time() + duration)
    # Отправляем сообщение о бане
    bot.send_message(chat_id, f"Пользователь {user_id} забанен на {duration} секунд.")

# Обработчик команды /ban
@bot.message_handler(commands=["ban"])
def ban_command(message: telebot.types.Message) -> None:
    # Проверяем, является ли отправитель команды администратором чата
    if not is_admin(message):
        bot.reply_to(message, "Вы не можете использовать эту команду, так как вы не являетесь администратором чата.")
        return
    # Проверяем, есть ли аргументы команды
    args = message.text.split()[1:]
    if len(args) != 2:
        bot.reply_to(message, "Неверный формат команды. Используйте /ban <user_id> <duration>, где user_id - идентификатор пользователя, а duration - продолжительность бана в секундах.")
        return
    # Проверяем, являются ли аргументы числами
    try:
        user_id = int(args[0])
        duration = int(args[1])
    except ValueError:
        bot.reply_to(message, "Неверный формат аргументов. Используйте /ban <user_id> <duration>, где user_id - идентификатор пользователя, а duration - продолжительность бана в секундах.")
        return
    # Проверяем, находится ли продолжительность бана в допустимом диапазоне
    if duration < 86400 or duration > 63072000:
        bot.reply_to(message, "Неверная продолжительность бана. Она должна быть от 1 дня до 2 лет, то есть от 86400 до 63072000 секунд.")
        return
    # Вызываем функцию для бана пользователя
    ban_user(message, user_id, duration)


# Функция для проверки, является ли пользователь администратором чата
def is_admin(message: telebot.types.Message) -> bool:
    chat_id = message.chat.id
    user_id = message.from_user.id
    # Получаем список администраторов чата
    admins = bot.get_chat_administrators(chat_id)
    # Проверяем, есть ли пользователь среди них
    for admin in admins:
        if admin.user.id == user_id:
            return True
    return False

# Функция для разбана пользователя
def unban_user(message: telebot.types.Message, user_id: int) -> None:
    chat_id = message.chat.id
    # Разбаниваем пользователя
    bot.unban_chat_member(chat_id, user_id)
    # Отправляем сообщение о разбане
    bot.send_message(chat_id, f"Пользователь {user_id} разбанен.")

# Обработчик команды /unban
@bot.message_handler(commands=["unban"])
def unban_command(message: telebot.types.Message) -> None:
    # Проверяем, является ли отправитель команды администратором чата
    if not is_admin(message):
        bot.reply_to(message, "Вы не можете использовать эту команду, так как вы не являетесь администратором чата.")
        return
    # Проверяем, есть ли аргумент команды
    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "Неверный формат команды. Используйте /unban <user_id>, где user_id - идентификатор пользователя.")
        return
    # Проверяем, является ли аргумент числом
    try:
        user_id = int(args[0])
    except ValueError:
        bot.reply_to(message, "Неверный формат аргумента. Используйте /unban <user_id>, где user_id - идентификатор пользователя.")
        return
    # Вызываем функцию для разбана пользователя
    unban_user(message, user_id)
    # Функция для проверки, является ли пользователь администратором или модератором чата
def is_staff(message: telebot.types.Message) -> bool:
    chat_id = message.chat.id
    user_id = message.from_user.id
    # Получаем список администраторов и модераторов чата
    staff = bot.get_chat_administrators(chat_id) + bot.get_chat_moderators(chat_id)
    # Проверяем, есть ли пользователь среди них
    for member in staff:
        if member.user.id == user_id:
            return True
    return False



# создаем словарь для хранения правил для каждого чата
rules = {}

# обрабатываем команду /setrules
@bot.message_handler(commands=["setrules"])
def set_rules(message):
    # проверяем, является ли отправитель администратором чата
    chat_id = message.chat.id
    user_id = message.from_user.id
    admins = bot.get_chat_administrators(chat_id)
    admin_ids = [admin.user.id for admin in admins]
    if user_id not in admin_ids:
        # если нет, то отправляем сообщение об ошибке
        bot.reply_to(message, "Вы должны быть администратором, чтобы установить правила.")
        return
    # получаем текст правил из сообщения
    text = message.text
    # проверяем, есть ли текст после команды
    if len(text.split()) == 1:
        # если нет, то отправляем сообщение с инструкцией
        bot.reply_to(message, "Пожалуйста, укажите правила после команды. Например:\n/setrules Не ругайтесь и не спамьте.")
        return
    # удаляем команду из текста
    rules_text = text.replace("/setrules", "").strip()
    # сохраняем правила в словаре
    rules[chat_id] = rules_text
    # отправляем сообщение с подтверждением
    bot.reply_to(message, f"Правила для этого чата установлены:\n{rules_text}")

# обрабатываем команду /rules
@bot.message_handler(commands=["rules"])
def show_rules(message):
    # получаем идентификатор чата
    chat_id = message.chat.id
    # проверяем, есть ли правила для этого чата в словаре
    if chat_id not in rules:
        # если нет, то отправляем сообщение с уведомлением
        bot.reply_to(message, "Для этого чата не установлены правила.")
        return
    # получаем правила из словаря
    rules_text = rules[chat_id]
    # отправляем правила в ответ на сообщение
    bot.reply_to(message, f"Правила для этого чата:\n{rules_text}")

# Запуск бота
bot.polling()