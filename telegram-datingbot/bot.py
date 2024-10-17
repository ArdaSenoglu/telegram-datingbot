from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, Updater, ConversationHandler, \
    CallbackContext, CallbackQueryHandler, filters, JobQueue, Job
from telegram.error import BadRequest
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InputFile,InlineKeyboardMarkup, KeyboardButton
import mysql.connector
from mysql.connector import pooling
import urllib.request
import requests
import os
import io
import random
import asyncio
import time as tm
import re
from typing import TYPE_CHECKING, Any, Generic, Optional, Tuple, Union, cast, overload
from telegram.ext._utils.types import CCT, JobCallback
from queue import Queue
from telegram import Bot

db = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "Users",
}
connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, pool_reset_session=True, **db)

Token = "YOUR_TOKEN"
Bot_UserName = "@YOUR_BOT_NAME"


NAME,AGE, GENDER, LOOKING, CITY, BIO, CHANGEBIO, PHOTO, SAVEPHOTO, SAVE_MESSAGE, SHOW_PROFILE, MENU_EXE, WAIT_MENU_EXE, MATCHING, DEACTIVE, SHOW_WHO_LIKES, NONEACTIVE,LANGUAGE,CHECK_USER_STATE,PREMIUM,LANGUAGE_COMMAND,REPORT_USER,BANNED = range(
    23)
gender_choice = {
    'Türkçe': ["Erkek", "Kız"],
    'English': ["Male", "Female"],
    'Русский': ["Я парень","Я девушка"],
    'Українська': ["Я хлопець","Я дівчина"]
}
looking_choice = {
    'Türkçe': ["Erkekler", "Kızlar"],
    'English': ["Boys", "Girls"],
    'Русский': ["Парни", "Деушки"],
    'Українська': ["Хлопці", "Дівчата"]
}
region_choice = {
    'Türkçe': ["Avrupa Yakası", "Istanbul Yakası"],
    'English': ["European side","Istanbul side"],
    'Русский': ["Европейская сторона", "Стамбул Сиде"],
    'Українська': ["Європейська сторона","Стамбул Сіде"]
}
leave_text_choice = {
    'Türkçe': ["Gec"],
    'English': ["Pass"],
    'Русский': ["Пропустить"],
    'Українська': ["Пропустити"],
}
yes_text = {
    'Türkçe': ["Evet"],
    'English': ["Yes"],
    'Русский': ["Да"],
    'Українська': ["Так"],
}
go_back_text = {
    'Türkçe': ["Geri dön"],
    'English': ["Go back"],
    'Русский': ["вернуться назад"],
    'Українська': ["Повернутися назад"],
}
leave_photo_choice = {
    'Türkçe': ["Mevcut fotoğrafı bırak"],
    'English': ["Leave current photo"],
    'Русский': ["Оставить текущее"],
    'Українська': ["Залишити поточне"],
}
menu_choice = [
    ["1", "2", "3", "4"],
]
wait_menu_choice = [
    ["1", "2", "3"],
]
like_choice = [
    ["❤️", "💌", "👎", "💤"],
]
like_or_not_choice = [
    ["❤️", "👎"],
]
report_user_choice = [
    ["1🔞","2💊","3💰","4🦨","9"]
]
show_n_not_show_choice = [
    ["1", "2"],
]
show_who_likes_choice = {
    'Türkçe': ["Göster.","Artık aramıyorum."],
    'English': ["Show.","Not searching anymore."],
    'Русский': ["Показать.","Не хочу больше никого смотреть."],
    'Українська': ["Показати.","Не хочу більше нікого дивитися."],
}
pay_choice = {
    'Türkçe': ["1 Aylık", "6 Aylık", "1 Yıllık", "Geri dön"],
    'English': ["1 Month", "6 Months", "1 Year","Go back"],
    'Русский': ["1 месяц", "6 месяцев", "1 год", "вернуться назад"],
    'Українська': ["1 місяць", "6 місяців", "1 рік", "Повернутися назад"]
}
show_profiles = {
    'Türkçe': ["Profilleri görüntüle."],
    'English': ["View profiles."],
    'Русский': ["Смотреть анкеты."],
    'Українська': ["Дивитися анкети."],
}
language_options =[
    ["🇬🇧 English"],["🇹🇷 Türkçe"],["🇷🇺 Русский"],["🇺🇦 Українська"]
]
language_choice_markup = ReplyKeyboardMarkup(language_options)
lang = {}
daily_user_id = {}
spams = {}
msgs = 7 # Messages in
max = 2 # Seconds
ban = 5 # Seconds

menu_markup = ReplyKeyboardMarkup(menu_choice, resize_keyboard=True, one_time_keyboard=True)
report_markup = ReplyKeyboardMarkup(report_user_choice,resize_keyboard=True, one_time_keyboard=True)

like_markup = ReplyKeyboardMarkup(like_choice, resize_keyboard=True, one_time_keyboard=True)

like_or_not_markup = ReplyKeyboardMarkup(like_or_not_choice, resize_keyboard=True, one_time_keyboard=True)

show_n_not_show_markup = ReplyKeyboardMarkup(show_n_not_show_choice, resize_keyboard=True, one_time_keyboard=True)

wait_menu_markup = ReplyKeyboardMarkup(wait_menu_choice, resize_keyboard=True, one_time_keyboard=True)

def is_spam(user_id):
    try:
        usr = spams[user_id]
        usr["messages"] += 1
    except:
        spams[user_id] = {"next_time": int(tm.time()) + max, "messages": 1, "banned": 0}
        usr = spams[user_id]
    if usr["banned"] >= int(tm.time()):
        return True
    else:
        if usr["next_time"] >= int(tm.time()):
            if usr["messages"] >= msgs:
                spams[user_id]["banned"] = tm.time() + ban
                # text = """You're banned for {} minutes""".format(ban/60)
                # bot.send_message(user_id, text)
                # User is banned! alert him...
                return True
        else:
            spams[user_id]["messages"] = 1
            spams[user_id]["next_time"] = int(tm.time()) + max
    return False


async def check_user_state(update: Update, context:CallbackContext):
    chat_id = update.effective_chat.id
    user_id = context.user_data.get(update.effective_user.id,chat_id)
    context.user_data['user_id'] = user_id
    daily_user_id[user_id] = context.user_data.get('user_id')
    await language_control(context)
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT Language FROM Users WHERE PersonID = %s",
        (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    if result == ('',):
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM Users WHERE PersonID = %s AND UserName IS NOT NULL AND Age IS NOT NULL AND Gender IS NOT NULL AND Looking IS NOT NULL AND City IS NOT NULL AND Bio IS NOT NULL AND Photo IS NOT NULL AND IsActive = 1",
            (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        user_exists = result[0] > 0
        if user_exists:
            await context.bot.send_message(user_id,'Please select your language:', reply_markup=language_choice_markup)
            return LANGUAGE
        else:
            await context.bot.send_message(user_id,'Please select your language:', reply_markup=language_choice_markup)
            return NAME


    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM Users WHERE PersonID = %s AND UserName IS NOT NULL AND Age IS NOT NULL AND Gender IS NOT NULL AND Looking IS NOT NULL AND City IS NOT NULL AND Bio IS NOT NULL AND Photo IS NOT NULL AND IsActive = 1",
        (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM Users WHERE PersonID = %s AND UserName IS NOT NULL AND Age IS NOT NULL AND Gender IS NOT NULL AND Looking IS NOT NULL AND City IS NOT NULL AND Bio IS NOT NULL AND Photo IS NOT NULL AND IsActive = 0",
        (user_id,))
    result_is_not_active = cursor.fetchone()
    cursor.close()
    conn.close()

    user_exists = result[0] > 0
    user_exists_is_not_active = result_is_not_active[0] > 0
    if user_exists:
        user_id = context.user_data.get('user_id')
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserName, Age, City, Bio, Photo, Premium FROM Users WHERE PersonID = %s", (user_id,))
        result = cursor.fetchone()
        user_name, user_age, user_city, user_bio, user_photo, user_premium = result
        cursor.close()
        conn.close()
        message_text = f"{user_name}, {user_age}, {user_city}, {user_bio if user_bio is not None else 'None'} {"| Premium ❤️‍🔥 " if user_premium > 0 else ''}"
        your_profile_messages = {
            'Türkçe': f"Profiliniz:",
            'English': f"Your profile:",
            'Русский': f"Так выглядит твоя анкета:",
            'Українська': f"Так виглядає твоя анкета:"
        }
        your_profile_message = your_profile_messages.get(lang.get(user_id, 0),
                                                         f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(your_profile_message)
        await update.message.reply_photo(f"{user_photo if user_photo is not None else 'None'}", caption=message_text)
        profile_messages = {
            'Türkçe': f"1. Profilimi Düzenle.\n"
                      f"2. Profil fotoğrafımı değiştir.\n"
                      f"3. Biografimi düzenle.\n"
                      f"4. Profilleri Görmeye Başla.",
            'English': f"1. Edit My Profile.\n"
                       f"2. Change My Profile Picture.\n"
                       f"3. Edit My Bio.\n"
                       f"4. Start Viewing Profiles.",
            'Русский': f"1. Заполнить анкету заново. \n"
                       f"2. Изменить фото.\n"
                       f"3. Изменить текст анкеты.\n"
                       f"4. Смотреть анкеты.",
            'Українська':f"1. Заповнити анкету наново.\n"
                         f"2. Змінити фото. \n"
                         f"3. Змінити текст анкети.\n"
                         f"4. Дивитися анкети."
        }
        profile_message = profile_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
        await context.bot.send_message(user_id,profile_message, reply_markup=menu_markup)

        return MENU_EXE
    elif user_exists_is_not_active:
        last_mes = context.user_data.get(context.user_data.get('user_id'), update.message.text)
        if last_mes == "Profilleri görüntüle." or last_mes == "View profiles." or last_mes == "Смотреть анкеты." or last_mes == "Дивитися анкети.":
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET IsActive = 1 WHERE PersonID = %s", (user_id,))
            cursor.close()
            conn.close()
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT UserName, Age, City, Bio, Photo, Premium FROM Users WHERE PersonID = %s", (user_id,))
            result = cursor.fetchone()
            user_name, user_age, user_city, user_bio, user_photo, user_premium = result
            cursor.close()
            conn.close()
            message_text = f"{user_name}, {user_age}, {user_city}, {user_bio if user_bio is not None else 'None'}  {"| Premium ❤️‍🔥 " if user_premium > 0 else ''}"
            your_profile_messages = {
                'Türkçe': f"Profiliniz:",
                'English': f"Your profile:",
                'Русский': f"Так выглядит твоя анкета:",
                'Українська': f"Так виглядає твоя анкета:"
            }
            your_profile_message = your_profile_messages.get(lang.get(user_id, 0),
                                                             f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(your_profile_message)
            await update.message.reply_photo(f"{user_photo if user_photo is not None else 'None'}",
                                             caption=message_text)
            profile_messages = {
                'Türkçe': f"1. Profilimi Düzenle.\n"
                          f"2. Profil fotoğrafımı değiştir.\n"
                          f"3. Biografimi düzenle.\n"
                          f"4. Profilleri Görmeye Başla.",
                'English': f"1. Edit My Profile.\n"
                           f"2. Change My Profile Picture.\n"
                           f"3. Edit My Bio.\n"
                           f"4. Start Viewing Profiles.",
                'Русский': f"1. Заполнить анкету заново. \n"
                           f"2. Изменить фото.\n"
                           f"3. Изменить текст анкеты.\n"
                           f"4. Смотреть анкеты.",
                'Українська': f"1. Заповнити анкету наново.\n"
                              f"2. Змінити фото. \n"
                              f"3. Змінити текст анкети.\n"
                              f"4. Дивитися анкети."
            }
            profile_message = profile_messages.get(lang.get(user_id, 0),
                                                   f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(profile_message, reply_markup=menu_markup)

            return MENU_EXE
        else:
            show_profiles_markup = show_profiles.get(lang.get(user_id, 0))
            show_profiles_markup = ReplyKeyboardMarkup([show_profiles_markup], resize_keyboard=True,
                                                       one_time_keyboard=True)
            wrong_value_messages = {
                'Türkçe': f"Yanlış bir değer girdiniz!",
                'English': f"You entered an incorrect value!",
                'Русский': f"Вы ввели неправильное значение!",
                'Українська': f"Ви ввели неправильне значення!"
            }
            wrong_value_message = wrong_value_messages.get(lang.get(user_id, 0),
                                                           f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(wrong_value_message,reply_markup=show_profiles_markup)
            end_messages = {
                'Türkçe': f"Umarım benim yardımımla biriyle tanışmışsınızdır!\nSohbet etmekten her zaman mutluluk duyarım. Sıkılırsanız bana mesaj atın - sizin için özel birini bulacağım.\n1. Profilleri görüntüle",
                'English': f"Hope you met someone with my help!\nAlways happy to chat. If bored, text me -  I'll find someone special for you.\n1. View profiles",
                'Русский': f"Надеюсь ты нашел кого-то благодаря мне!\nРад был с тобой пообщаться, будет скучно – пиши, обязательно найдем тебе кого-нибудь\n1. Смотреть анкеты",
                'Українська': f"Сподіваюсь ти когось знайшов з моєю допомогою!\nРадий був поспілкуватися, якщо буде нудно – пиши, обов'язково знайдем тобі когось\n1. Дивитися анкети"
            }
            end_message = end_messages.get(lang.get(user_id, 0),
                                           f"Unsupported language: {lang.get(user_id, 0)}")
            show_profiles_markup = show_profiles.get(lang.get(user_id, 0))
            show_profiles_markup = ReplyKeyboardMarkup([show_profiles_markup], resize_keyboard=True,
                                                       one_time_keyboard=True)
            await update.message.reply_text(end_message, reply_markup=show_profiles_markup)
            return NONEACTIVE
    else:
        await context.bot.send_message(user_id,'Please select your language:', reply_markup=language_choice_markup)
        return NAME
async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (context.user_data.get('user_id'),))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(context.user_data.get('user_id'), "You Are banned!")
        return BANNED
    await context.bot.send_message(context.user_data.get('user_id'), 'Please select your language:', reply_markup=language_choice_markup)
    return LANGUAGE
async def language(update:Update,context:CallbackContext):
    lange = re.sub(r'^[^\w]+', '', context.user_data.get(context.user_data.get('user_id'), update.message.text))
    if lange != "Türkçe" and lange != "English" and lange != "Русский" and lange != "Українська":
        await update.message.reply_text("Please enter a valid Language")
        return LANGUAGE
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM Users WHERE PersonID = %s AND UserName IS NOT NULL AND Age IS NOT NULL AND Gender IS NOT NULL AND Looking IS NOT NULL AND City IS NOT NULL AND Bio IS NOT NULL AND Photo IS NOT NULL AND IsActive = 1",
        (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    user_exists = result[0] > 0
    await language_control(context)
    if user_exists:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Users SET Language = %s, IsActive = %s WHERE PersonID = %s", (lange, 1, user_id))
        cursor.close()
        conn.close()
        user_id = context.user_data.get('user_id')
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserName, Age, City, Bio, Photo, Premium FROM Users WHERE PersonID = %s", (user_id,))
        result = cursor.fetchone()
        user_name, user_age, user_city, user_bio, user_photo, user_premium = result
        cursor.close()
        conn.close()
        message_text = f"{user_name}, {user_age}, {user_city}, {user_bio if user_bio is not None else 'None'}  {"| Premium ❤️‍🔥 " if user_premium > 0 else ''}"
        your_profile_messages = {
            'Türkçe': f"Profiliniz:",
            'English': f"Your profile:",
            'Русский': f"Так выглядит твоя анкета:",
            'Українська': f"Так виглядає твоя анкета:"
        }
        your_profile_message = your_profile_messages.get(lange, f"Unsupported language: {lang}")
        await context.bot.send_message(user_id,your_profile_message)
        await context.bot.send_photo(user_id,f"{user_photo if user_photo is not None else 'None'}",caption=message_text)
        profile_messages = {
            'Türkçe': f"1. Profilimi Düzenle.\n"
                      f"2. Profil fotoğrafımı değiştir.\n"
                      f"3. Biografimi düzenle.\n"
                      f"4. Profilleri Görmeye Başla.",
            'English': f"1. Edit My Profile.\n"
                       f"2. Change My Profile Picture.\n"
                       f"3. Edit My Bio.\n"
                       f"4. Start Viewing Profiles.",
            'Русский': f"1. Заполнить анкету заново. \n"
                       f"2. Изменить фото.\n"
                       f"3. Изменить текст анкеты.\n"
                       f"4. Смотреть анкеты.",
            'Українська':f"1. Заповнити анкету наново.\n"
                         f"2. Змінити фото. \n"
                         f"3. Змінити текст анкети.\n"
                         f"4. Дивитися анкети."
        }

        profile_message = profile_messages.get(lange, f"Unsupported language: {lange}")
        await context.bot.send_message(user_id,profile_message, reply_markup=menu_markup)
        return MENU_EXE
    else:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT PersonID FROM Users WHERE PersonID = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET Language = %s, IsActive = %s WHERE PersonID = %s", (lange, 1, user_id))
            cursor.close()
            conn.close()
        else:
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Users (PersonID, Language,IsActive) VALUES (%s, %s,%s)", (user_id, lange, 1))
            cursor.close()
            conn.close()
        messages = {
            'Türkçe': f"Merhaba {Bot_UserName}'a Hoşgeldiniz! Başlamadan önce, Bana isminizi söyleyebilirmisiniz...",
            'English': f"Hello! Welcome to {Bot_UserName}! Before we start, can you tell me your name?",
            'Русский': f"Привет! Добро пожаловать в {Bot_UserName}! Прежде чем мы начнем, вы можете сказать мне свое имя?",
            'Українська': f"Привіт! Ласкаво просимо до {Bot_UserName}! Перш ніж ми почнемо, ви можете сказати мені своє ім'я?",
        }
        message = messages.get(lange, f"Unsupported language: {lange}")
        await update.message.reply_text(message)
        return AGE


async def set_name(update:Update,context:CallbackContext):
    lang = re.sub(r'^[^\w]+', '', context.user_data.get(context.user_data.get('user_id'), update.message.text))
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT PersonID FROM Users WHERE PersonID = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Users SET Language = %s, IsActive = %s WHERE PersonID = %s", (lang, 1, user_id))
        cursor.close()
        conn.close()
    else:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (PersonID, Language,IsActive) VALUES (%s, %s,%s)", (user_id, lang, 1))
        cursor.close()
        conn.close()
    messages = {
        'Türkçe': f"Merhaba {Bot_UserName}'a Hoşgeldiniz! Başlamadan önce, Bana isminizi söyleyebilirmisiniz...",
        'English': f"Hello! Welcome to {Bot_UserName}! Before we start, can you tell me your name?",
        'Русский': f"Привет! Добро пожаловать в {Bot_UserName}! Прежде чем мы начнем, вы можете сказать мне свое имя?",
        'Українська': f"Привіт! Ласкаво просимо до {Bot_UserName}! Перш ніж ми почнемо, ви можете сказати мені своє ім'я?",
    }
    message = messages.get(lang, f"Unsupported language: {lang}")
    await update.message.reply_text(message)
    return AGE
async def start_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    daily_user_id[user_id] = user_id
    await update.message.reply_text(
            f"Merhaba {Bot_UserName}'a Hoşgeldiniz! Başlamadan önce, Bana isminizi söyleyebilirmisiniz...")
    return AGE


async def set_age(update: Update, context: CallbackContext):
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (context.user_data.get('user_id'),))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(context.user_data.get('user_id'), "You Are banned!")
        return BANNED
    if context.user_data.get(context.user_data.get('user_id'), update.message.text) == "/language":
        await context.bot.send_message(context.user_data.get('user_id'), 'Please select your language:', reply_markup=language_choice_markup)
        return LANGUAGE
    elif re.search(r'\d|\W|\s', context.user_data.get(context.user_data.get('user_id'), update.message.text)):
        await context.bot.send_message(context.user_data.get('user_id'), "Lütfen geçerli bir isim söyleyin!")
        return AGE
    user_name = context.user_data.get(context.user_data.get('user_id'), update.message.text)
    context.user_data['user_name'] = user_name
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT PersonID FROM Users WHERE PersonID = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Users SET UserName = %s, IsActive = %s WHERE PersonID = %s", (user_name, 1, user_id))
        cursor.close()
        conn.close()
    else:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (PersonID, UserName,IsActive) VALUES (%s, %s,%s)", (user_id, user_name, 1))
        cursor.close()
        conn.close()
    await language_control(context)
    messages_first = {
        'Türkçe': f"Hoşgeldin, {user_name}! Başlamadan önce profilini oluşturalım. \U0001F60B",
        'English': f"Hello, {user_name}! Before we start, let's create your profile. \U0001F60B",
        'Русский': f"Привет, {user_name}! Давайте создадим ваш профиль перед тем, как начать. \U0001F60B",
        'Українська': f"Привіт, {user_name}! Давайте створимо ваш профіль, перш ніж почнемо. \U0001F60B",
    }
    messages_second = {
        'Türkçe': f"{user_name}, yaşın kaç?",
        'English': f"{user_name}, how old are you?",
        'Русский': f"{user_name}, сколько тебе лет?",
        'Українська': f"{user_name}, скільки тебе років?",
    }
    message_first = messages_first.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
    message_second = messages_second.get(lang.get(user_id,0),f"Unsupported language: {lang.get(user_id, 0)}")
    await update.message.reply_text(message_first)
    await update.message.reply_text(message_second)
    return GENDER


async def set_gender(update: Update, context: CallbackContext):
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    markup = gender_choice.get(lang.get(user_id, 0))
    markup = ReplyKeyboardMarkup([markup], resize_keyboard=True, one_time_keyboard=True)
    messages_wrong = {
        'Türkçe': f"Lütfen geçerli bir yaş giriniz!",
        'English': f"Please enter a valid age!",
        'Русский': f"Пожалуйста, введите действительный возраст!",
        'Українська': f"Будь ласка, введіть дійсний вік!",
    }
    messages_wrong_age = {
        'Türkçe': f"18 yaşından küçükseniz bu bot içerisinde bulunamazsınız!!!",
        'English': f"If you are under 18 years of age you cannot be in this bot!!!",
        'Русский': f"Если вам меньше 18 лет, вы не можете участвовать в этом боте!!!",
        'Українська': f"Якщо вам менше 18 років, ви не можете брати участь у цьому боті!!!",
    }
    message_wrong_age = messages_wrong_age.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
    message_wrong = messages_wrong.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
    user_age = context.user_data.get(context.user_data.get('user_id'), update.message.text)
    context.user_data['user_age'] = user_age
    if context.user_data.get(context.user_data.get('user_id'), update.message.text) == "/language":
        await context.bot.send_message(user_id, 'Please select your language:', reply_markup=language_choice_markup)
        return LANGUAGE
    try:
        user_age = int(user_age)
    except ValueError:
        await update.message.reply_text(message_wrong)
        return GENDER
    if user_age < 18:
        await update.message.reply_text(message_wrong_age)
        await update.message.reply_text(message_wrong)
        return GENDER
    elif user_age > 99:
        message = messages_wrong.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(message)
        return GENDER
    else:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Users SET Age = %s WHERE PersonID = %s", (user_age, user_id))
        cursor.close()
        conn.close()
        messages = {
            'Türkçe': f"Cinsiyetiniz nedir?",
            'English': f"Specify your gender",
            'Русский': f"Теперь определимся с полом",
            'Українська': f"Тепер оберемо стать",
        }
        message = messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(message, reply_markup=markup)
        return LOOKING


async def set_looking(update: Update, context: CallbackContext):
    user_gender = context.user_data.get(context.user_data.get('user_id'), update.message.text)
    if user_gender == "Male" or user_gender == "Я парень" or user_gender == "Я хлопець":
        user_gender = "Erkek"
    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "/language":
        await context.bot.send_message(context.user_data.get('user_id'), 'Please select your language:', reply_markup=language_choice_markup)
        return LANGUAGE
    elif user_gender == "Female" or user_gender == "Я девушка" or user_gender == "Я дівчина":
        user_gender = "Kız"
    context.user_data['user_gender'] = user_gender
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    looking_markup = looking_choice.get(lang.get(user_id, 0))
    looking_markup = ReplyKeyboardMarkup([looking_markup], resize_keyboard=True, one_time_keyboard=True)
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET Gender = %s WHERE PersonID = %s", (user_gender, user_id))
    cursor.close()
    conn.close()
    messages = {
        'Türkçe': f"Kimlerle ilgileniyorsunuz?",
        'English': f"Who are you looking for?",
        'Русский': f"Кто тебе интересен?",
        'Українська': f"Хто тебе цікавить?",
    }
    message = messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
    await update.message.reply_text(message, reply_markup=looking_markup)
    return CITY


async def set_city(update: Update, context: CallbackContext):
    if context.user_data.get(context.user_data.get('user_id'), update.message.text) == "/language":
        await context.bot.send_message(context.user_data.get('user_id'), 'Please select your language:', reply_markup=language_choice_markup)
        return LANGUAGE
    user_looking = context.user_data.get(context.user_data.get('user_id'), update.message.text)
    if user_looking == "Boys" or user_looking == "Парни"or user_looking == "Хлопці":
        user_looking = "Erkekler"
    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "/language":
        await context.bot.send_message(context.user_data.get('user_id'), 'Please select your language:', reply_markup=language_choice_markup)
        return LANGUAGE
    elif user_looking == "Girls" or user_looking == "Деушки" or user_looking == "Дівчата":
        user_looking = "Kızlar"
    context.user_data['user_looking'] = user_looking
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    region_markup = region_choice.get(lang.get(user_id, 0))
    region_markup = ReplyKeyboardMarkup([region_markup], resize_keyboard=True, one_time_keyboard=True)
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET Looking = %s WHERE PersonID = %s", (user_looking, user_id))
    cursor.close()
    conn.close()
    messages = {
        'Türkçe': f"Biyografinize eklemem için kendinizden biraz daha bahsedin.En iyi eşleşmeleri sizin için bulacağım.",
        'English': f"Tell more about yourself. Who are you looking for? What do you want to do? I'll find the best matches.",
        'Русский': f"Расскажи о себе и кого хочешь найти, чем предлагаешь заняться. Это поможет лучше подобрать тебе компанию.",
        'Українська': f"Розкажи про себе, кого хочеш знайти, чим пропонуєш зайнятись. Це допоможе краще підібрати тобі компанію.",
    }
    message = messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
    leave_current_markup = leave_text_choice.get(lang.get(user_id, 0))
    leave_current_markup = ReplyKeyboardMarkup([leave_current_markup], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(message,reply_markup=leave_current_markup)
    return PHOTO


async def set_bio(update: Update, context: CallbackContext):
    if context.user_data.get(context.user_data.get('user_id'), update.message.text) == "/language":
        await context.bot.send_message(context.user_data.get('user_id'), 'Please select your language:', reply_markup=language_choice_markup)
        return LANGUAGE
    user_city = context.user_data.get(context.user_data.get('user_id'), update.message.text)
    if user_city == "European side" or user_city == "Европейская сторона" or user_city == "Європейська сторона":
        user_city = "Avrupa Yakası"
    elif user_city == "Istanbul side" or user_city == "Стамбул Сиде" or user_city == "Стамбул Сіде":
        user_city = "Istanbul Yakası"
    context.user_data['user_city'] = user_city
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    leave_current_markup = leave_text_choice.get(lang.get(user_id, 0))
    leave_current_markup = ReplyKeyboardMarkup([leave_current_markup], resize_keyboard=True, one_time_keyboard=True)
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET City = %s WHERE PersonID = %s", (user_city, user_id))
    cursor.close()
    conn.close()
    messages = {
        'Türkçe': f"Biyografinize eklemem için kendinizden biraz daha bahsedin.En iyi eşleşmeleri sizin için bulacağım.",
        'English': f"Tell more about yourself. Who are you looking for? What do you want to do? I'll find the best matches.",
        'Русский': f"Расскажи о себе и кого хочешь найти, чем предлагаешь заняться. Это поможет лучше подобрать тебе компанию.",
        'Українська': f"Розкажи про себе, кого хочеш знайти, чим пропонуєш зайнятись. Це допоможе краще підібрати тобі компанію.",
    }
    message = messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
    await update.message.reply_text(message,reply_markup=leave_current_markup)
    return PHOTO


async def set_photo(update: Update, context: CallbackContext):
    await language_control(context)
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    leave_current_photo_markup = leave_photo_choice.get(lang.get(user_id, 0))
    leave_current_photo_markup = ReplyKeyboardMarkup([leave_current_photo_markup], resize_keyboard=True,
                                                     one_time_keyboard=True)
    last_mes = context.user_data.get(context.user_data.get('user_id'), update.message.text)
    if last_mes == "Gec" or last_mes == "Pass" or last_mes == "Пропустить" or last_mes == "Пропустити":
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Bio FROM Users WHERE PersonID = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result and result[0] is not None:
            messages = {
                'Türkçe': f"Diğer kullanıcıların görmesi için fotoğrafınızı👍gönderin.",
                'English': f"Send your photo👍 for other users to see",
                'Русский': f"Теперь пришли фото👍, его будут видеть другие пользователи",
                'Українська': f"Тепер надішли фото 👍, його побачать інші користувачі",
            }
            message = messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(message,
                                            reply_markup=leave_current_photo_markup)
        else:
            user_id = context.user_data.get('user_id')
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET Bio = %s WHERE PersonID = %s", (".", user_id))
            cursor.close()
            conn.close()
            messages = {
                'Türkçe': f"Diğer kullanıcıların görmesi için fotoğrafınızı👍gönderin.",
                'English': f"Send your photo👍 for other users to see",
                'Русский': f"Теперь пришли фото👍, его будут видеть другие пользователи",
                'Українська': f"Тепер надішли фото 👍, його побачать інші користувачі",
            }
            message = messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(message,
                                            reply_markup=leave_current_photo_markup)
        return SAVEPHOTO
    else:
        user_bio = context.user_data.get(context.user_data.get('user_id'), update.message.text)
        context.user_data['user_bio'] = user_bio
        user_id = context.user_data.get('user_id')
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Users SET Bio = %s WHERE PersonID = %s", (user_bio, user_id))
        cursor.close()
        conn.close()
        messages = {
            'Türkçe': f"Diğer kullanıcıların görmesi için fotoğrafınızı👍gönderin.",
            'English': f"Send your photo👍 for other users to see",
            'Русский': f"Теперь пришли фото👍, его будут видеть другие пользователи",
            'Українська': f"Тепер надішли фото 👍, його побачать інші користувачі",
        }
        message = messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(message,
                                        reply_markup=leave_current_photo_markup)
    return SAVEPHOTO


async def save_photo(update: Update, context: CallbackContext):
    await language_control(context)
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    yes_markup = yes_text.get(lang.get(user_id, 0))
    yes_markup = ReplyKeyboardMarkup([yes_markup], resize_keyboard=True, one_time_keyboard=True)
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Photo FROM Users WHERE PersonID = %s", (user_id,))
    photo_control = cursor.fetchone()
    cursor.close()
    conn.close()
    last_mes = context.user_data.get(context.user_data.get('user_id'), update.message.text)
    if last_mes == "Mevcut fotoğrafı bırak" or last_mes == "Leave current photo" or last_mes == "Оставить текущее"or last_mes == "Залишити поточне":
        if photo_control and photo_control[0] is not None:
            messages = {
                'Türkçe': f"Profiliniz Hazır Devam etmeye Hazırmısınız?",
                'English': f"Your profile is ready Are you ready to continue?",
                'Русский': f"Ваш профиль готов. Готовы двигаться дальше?",
                'Українська': f"Ваш профіль готовий. Готові рухатися далі?",
            }
            message = messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(message, reply_markup=yes_markup)
            return SHOW_PROFILE
        else:
            not_registered_photo_messages = {
                'Türkçe': f"Kayıtlı fotoğrafınız bulunmamaktadır lütfen bir fotoğraf ekleyin",
                'English': f"You do not have a saved photo, please send me a photo so I can save it to your profile",
                'Русский': f"У тебя нет сохраненной фотографии, пожалуйста, пришли мне фотографию, чтобы я мог сохранить ее в твоем профиле",
                'Українська': f"У тебе немає збереженої фотографії, будь ласка, надішли мені фотографію, щоб я міг зберегти її у твоєму профілі",
            }
            not_registered_photo_message = not_registered_photo_messages.get(lang.get(user_id, 0),
                                                                   f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(not_registered_photo_message)
            return SAVEPHOTO
    else:
        user_id = context.user_data.get('user_id')
        if update.message.photo:

            user_photo = update.message.photo[-1]
            file = await context.bot.get_file(user_photo.file_id)
            max_file_size_mb = 100
            if file.file_size > max_file_size_mb * 1024 * 1024:
                not_valid_size_messages = {
                    'Türkçe': f"Geçersiz dosya boyutu! Dosya boyutu {max_file_size_mb} MB'dan küçük olmalı.",
                    'English': f"Invalid file size! File size should be less than {max_file_size_mb} MB.",
                    'Русский': f"Недопустимый размер файла! Размер файла должен быть менее {max_file_size_mb} МБ.",
                    'Українська': f"Неприпустимий розмір файлу! Розмір файлу повинен бути менше {max_file_size_mb} МБ.",
                }
                not_valid_size_message = not_valid_size_messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
                await update.message.reply_text(not_valid_size_message)
                return SAVEPHOTO
            file_id = user_photo.file_id
            file_url = file.file_path
            photo_url = f"root_folder/user_photos/{user_id}/{user_id}.png"
            os.makedirs(os.path.dirname(photo_url), exist_ok=True)
            response = requests.get(file_url)
            with open(photo_url, 'wb') as file:
                file.write(response.content)
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET Photo = %s WHERE PersonID = %s", (photo_url, user_id))
            cursor.close()
            conn.close()
            ready_messages = {
                'Türkçe': f"Profiliniz Hazır Devam etmeye Hazırmısınız?",
                'English': f"Your profile is ready Are you ready to continue?",
                'Русский': f"Ваш профиль готов. Готовы двигаться дальше?",
                'Українська': f"Ваш профіль готовий. Готові рухатися далі?",
            }
            ready_message = ready_messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(ready_message, reply_markup=yes_markup)

            return SHOW_PROFILE
        else:
            not_valid_messages = {
                'Türkçe': f"Geçersiz bir dosya gönderdiniz!",
                'English': f"You have submitted an invalid file!",
                'Русский': f"Ты отправил недопустимый файл!",
                'Українська': f"Ти надіслав неприпустимий файл!",
            }
            not_valid_message = not_valid_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(not_valid_message)
            return SAVEPHOTO


async def change_bio(update: Update, context: CallbackContext):
    await language_control(context)
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    yes_markup = yes_text.get(lang.get(user_id, 0))
    yes_markup = ReplyKeyboardMarkup([yes_markup], resize_keyboard=True, one_time_keyboard=True)
    last_mes = context.user_data.get(context.user_data.get('user_id'), update.message.text)
    if last_mes == "Gec" or last_mes == "Pass" or last_mes == "Пропустить" or last_mes == "Пропустити":
        user_id = context.user_data.get('user_id')
        ready_messages = {
            'Türkçe': f"Profiliniz Hazır Devam etmeye Hazırmısınız?",
            'English': f"Your profile is ready Are you ready to continue?",
            'Русский': f"Ваш профиль готов. Готовы двигаться дальше?",
            'Українська': f"Ваш профіль готовий. Готові рухатися далі?",
        }
        ready_message = ready_messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(ready_message, reply_markup=yes_markup)
    else:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        user_bio = context.user_data.get(context.user_data.get('user_id'), update.message.text)
        context.user_data['user_bio'] = user_bio
        user_id = context.user_data.get('user_id')
        cursor.execute("UPDATE Users SET Bio = %s WHERE PersonID = %s", (user_bio, user_id))
        cursor.close()
        conn.close()
        ready_messages = {
            'Türkçe': f"Profiliniz Hazır Devam etmeye Hazırmısınız?",
            'English': f"Your profile is ready Are you ready to continue?",
            'Русский': f"Ваш профиль готов. Готовы двигаться дальше?",
            'Українська': f"Ваш профіль готовий. Готові рухатися далі?",
        }
        ready_message = ready_messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(ready_message, reply_markup=yes_markup)

    return SHOW_PROFILE


async def show_profile(update: Update, context: CallbackContext):
    await language_control(context)
    user_id = update.effective_user.id
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    last_mes = context.user_data.get(context.user_data.get('user_id'), update.message.text)
    if last_mes != "Evet" and last_mes != "Yes" and last_mes != "Да"and last_mes != "Так" and last_mes != "Geri dön" and last_mes != "Go back" and last_mes != "вернуться назад" and last_mes != "Повернутися назад" and last_mes != "/language":
        user_id = context.user_data.get('user_id')
        wrong_value_messages = {
            'Türkçe': f"Yanlış bir değer girdiniz!",
            'English': f"You entered a wrong value!",
            'Русский': f"Ты ввел неправильное значение!",
            'Українська': f"Ти ввів неправильне значення!",
        }
        wrong_value_message = wrong_value_messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
        go_back_text_markup = go_back_text.get(lang.get(user_id, 0))
        go_back_text_markup = ReplyKeyboardMarkup([go_back_text_markup], resize_keyboard=True,
                                                  one_time_keyboard=True)
        await update.message.reply_text(wrong_value_message,reply_markup=go_back_text_markup)
    if context.user_data.get(context.user_data.get('user_id'), update.message.text) == "/language":
        await context.bot.send_message(context.user_data.get('user_id'), 'Please select your language:', reply_markup=language_choice_markup)
        return LANGUAGE
    else:
        user_id = context.user_data.get('user_id')
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserName, Age, Bio, Photo, Premium FROM Users WHERE PersonID = %s", (user_id,))
        result = cursor.fetchone()
        user_name, user_age, user_bio, user_photo, user_premium = result
        cursor.close()
        conn.close()
        message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}  {"| Premium ❤️‍🔥 " if user_premium > 0 else ''}"
        your_profile_messages = {
            'Türkçe': f"Profiliniz:",
            'English': f"Your profile:",
            'Русский': f"Так выглядит твоя анкета:",
            'Українська': f"Так виглядає твоя анкета:"
        }
        your_profile_message = your_profile_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(your_profile_message)
        await update.message.reply_photo(f"{user_photo if user_photo is not None else 'None'}", caption=message_text)
        profile_messages = {
            'Türkçe': f"1. Profilimi Düzenle.\n"
                      f"2. Profil fotoğrafımı değiştir.\n"
                      f"3. Biografimi düzenle.\n"
                      f"4. Profilleri Görmeye Başla.",
            'English': f"1. Edit My Profile.\n"
                       f"2. Change My Profile Picture.\n"
                       f"3. Edit My Bio.\n"
                       f"4. Start Viewing Profiles.",
            'Русский': f"1. Заполнить анкету заново. \n"
                       f"2. Изменить фото.\n"
                       f"3. Изменить текст анкеты.\n"
                       f"4. Смотреть анкеты.",
            'Українська':f"1. Заповнити анкету наново.\n"
                         f"2. Змінити фото. \n"
                         f"3. Змінити текст анкети.\n"
                         f"4. Дивитися анкети."
        }
        profile_message = profile_messages.get(lang.get(user_id, 0),
                                                       f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(profile_message, reply_markup=menu_markup)

        return MENU_EXE


async def menu_exe(update: Update, context: CallbackContext):
    await language_control(context)
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    user_id = update.effective_user.id
    cursor.execute("SELECT LikeUserID FROM Likes WHERE LikedUserID = %s", (user_id,))
    likes = cursor.fetchall()
    cursor.close()
    conn.close()
    len_likes = len(likes)
    if context.user_data.get(context.user_data.get('user_id'), update.message.text) == "1":
        current_jobs = context.job_queue.get_jobs_by_name(name="dgc")
        for job in current_jobs:
            job.schedule_removal()
        messages = {
            'Türkçe': f"İsminiz nedir?",
            'English': f"What is your name?",
            'Русский': f"Как тебя зовут?",
            'Українська': f"Як тебе звати?",
        }
        message = messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(message)
        return AGE
    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "2":
        current_jobs = context.job_queue.get_jobs_by_name(name="dgc")
        for job in current_jobs:
            job.schedule_removal()
        messages = {
            'Türkçe': f"Diğer kullanıcıların görmesi için fotoğrafınızı👍gönderin.",
            'English': f"Send your photo👍 for other users to see",
            'Русский': f"Теперь пришли фото👍, его будут видеть другие пользователи",
            'Українська': f"Тепер надішли фото 👍, його побачать інші користувачі",
        }
        message = messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
        leave_current_photo_markup = leave_photo_choice.get(lang.get(user_id, 0))
        leave_current_photo_markup = ReplyKeyboardMarkup([leave_current_photo_markup], resize_keyboard=True,
                                                         one_time_keyboard=True)
        await update.message.reply_text(message,reply_markup=leave_current_photo_markup)
        return SAVEPHOTO
    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "3":
        current_jobs = context.job_queue.get_jobs_by_name(name="dgc")
        for job in current_jobs:
            job.schedule_removal()
        messages = {
            'Türkçe': f"Biyografinize eklemem için kendinizden biraz daha bahsedin.En iyi eşleşmeleri sizin için bulacağım.",
            'English': f"Tell more about yourself. Who are you looking for? What do you want to do? I'll find the best matches.",
            'Русский': f"Расскажи о себе и кого хочешь найти, чем предлагаешь заняться. Это поможет лучше подобрать тебе компанию.",
            'Українська': f"Розкажи про себе, кого хочеш знайти, чим пропонуєш зайнятись. Це допоможе краще підібрати тобі компанію.",
        }
        message = messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
        leave_current_markup = leave_text_choice.get(lang.get(user_id, 0))
        leave_current_markup = ReplyKeyboardMarkup([leave_current_markup], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(message,reply_markup=leave_current_markup)
        return CHANGEBIO
    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "4":
        ready_to_messages = {
            'Türkçe': f"Profilleri Görmeye Hazırmısın? 🥰",
            'English': f"Are You Ready to See Profiles? 🥰",
            'Русский': f"Готовы увидеть анкеты? 🥰",
            'Українська': f"Готові побачити анкети? 🥰",
        }
        ready_to_message = ready_to_messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
        yes_markup = yes_text.get(lang.get(user_id, 0))
        yes_markup = ReplyKeyboardMarkup([yes_markup], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(ready_to_message, reply_markup=yes_markup)
        is_spam(update.effective_user.id)
        return MATCHING
    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Göster." or context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Show." or context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Показать." or context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Показати." and len_likes> 0:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT PersonID, UserName, Age, Bio, Photo FROM Users JOIN Likes ON PersonID = LikeUserID WHERE LikedUserID = %s",
            (user_id,))
        liked_users = cursor.fetchall()[0]
        cursor.close()
        conn.close()
        userid, user_name, user_age, user_bio, user_photo = liked_users
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MesToPerson FROM Likes WHERE LikeUserID = %s AND LikedUserID = %s",
            (userid, user_id))
        mes_to_person_result = cursor.fetchone()
        mes_to_person = mes_to_person_result[0]
        cursor.close()
        conn.close()
        if mes_to_person is not None and mes_to_person != 'None':
            message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}\n\n\n Bu kişinin size bir mesajı var:\n {mes_to_person}"
        else:
            message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}"
        await update.message.reply_photo(user_photo, caption=message_text, reply_markup=like_or_not_markup)
        return SHOW_WHO_LIKES
    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Artık aramıyorum." or context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Not searching anymore." or context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Не хочу больше никого смотреть." or context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Не хочу більше нікого дивитися." and len_likes> 0:
        freeze_profile_messages = {
            'Türkçe': f"Hesabınızı dondurmak istiyormusnuz?\n\n\n1. Evet\n2. Geri dön",
            'English': f"You won't know who likes you then... Sure about deactivating?\n\n\n1. Yes, deactivate my profile please.\n2. No, I want to see my matches.",
            'Русский': f"Так ты не узнаешь, что кому-то нравишься... Точно хочешь отключить свою анкету?\n\n\n1. Да, отключить анкету.\n2. Нет, вернуться назад.",
            'Українська': f"Так ти не дізнаєшся, що комусь подобаєшся... Точно хочеш відключити свою анкету?\n\n\n1. Так, відключити анкету..\n2. Ні, повернутись назад."
        }
        freeze_profile_message = freeze_profile_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(freeze_profile_message,
                                        reply_markup=show_n_not_show_markup)
        return DEACTIVE
    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "/language":
        await context.bot.send_message(user_id, 'Please select your language:', reply_markup=language_choice_markup)
        return LANGUAGE
    elif context.user_data.get(context.user_data.get('user_id'),update.message.text) == "/report":
        no_report_here_messages = {
            'Türkçe': f"Sadece profiller şikayet edeblirsiniz.",
            'English': f"Works only on someone's profile",
            'Русский': f"Жалобу можно оставить только при просмотре анкеты",
            'Українська': f"Скаргу можна залишити тільки підчас перегляду анкет"
        }
        no_report_here_message = no_report_here_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(no_report_here_message)
    else:
        wrong_value_messages = {
            'Türkçe': f"Yanlış bir değer girdiniz!",
            'English': f"You entered an incorrect value!",
            'Русский': f"Вы ввели неправильное значение!",
            'Українська': f"Ви ввели неправильне значення!"
        }
        wrong_value_message = wrong_value_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(wrong_value_message,reply_markup=menu_markup)
        return MENU_EXE

async def wait_menu_exe(update: Update, context: CallbackContext):
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    yes_markup = yes_text.get(lang.get(user_id, 0))
    yes_markup = ReplyKeyboardMarkup([yes_markup], resize_keyboard=True, one_time_keyboard=True)
    if context.user_data.get(context.user_data.get('user_id'), update.message.text) == "1":
        ready_to_messages = {
            'Türkçe': f"Profilleri Görmeye Hazırmısın? 🥰",
            'English': f"Are You Ready to See Profiles? 🥰",
            'Русский': f"Готовы увидеть анкеты? 🥰",
            'Українська': f"Готові побачити анкети? 🥰",
        }
        ready_to_message = ready_to_messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(ready_to_message, reply_markup=yes_markup)
        return MATCHING
    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "2":
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserName, Age, Bio, Photo, Premium FROM Users WHERE PersonID = %s", (user_id,))
        result = cursor.fetchone()
        user_name, user_age, user_bio, user_photo, user_premium = result
        cursor.close()
        conn.close()
        message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}  {"| Premium ❤️‍🔥 " if user_premium > 0 else ''}"
        your_profile_messages = {
            'Türkçe':f"Profiliniz:",
            'English':f"Your profile:",
            'Русский': f"Так выглядит твоя анкета:",
            'Українська': f"Так виглядає твоя анкета:"
        }
        your_profile_message = your_profile_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(your_profile_message)
        await update.message.reply_photo(f"{user_photo if user_photo is not None else 'None'}", caption=message_text)
        profile_messages = {
            'Türkçe': f"1. Profilimi Düzenle.\n"
                      f"2. Profil fotoğrafımı değiştir.\n"
                      f"3. Biografimi düzenle.\n"
                      f"4. Profilleri Görmeye Başla.",
            'English': f"1. Edit My Profile.\n"
                       f"2. Change My Profile Picture.\n"
                       f"3. Edit My Bio.\n"
                       f"4. Start Viewing Profiles.",
            'Русский': f"1. Заполнить анкету заново. \n"
                       f"2. Изменить фото.\n"
                       f"3. Изменить текст анкеты.\n"
                       f"4. Смотреть анкеты.",
            'Українська':f"1. Заповнити анкету наново.\n"
                         f"2. Змінити фото. \n"
                         f"3. Змінити текст анкети.\n"
                         f"4. Дивитися анкети."
        }
        profile_message = profile_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(profile_message, reply_markup=menu_markup)

        return MENU_EXE
    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "3":
        freeze_profile_messages = {
            'Türkçe': f"Hesabınızı dondurmak istiyormusnuz?\n\n\n1. Evet\n2. Geri dön",
            'English': f"You won't know who likes you then... Sure about deactivating?\n\n\n1. Yes, deactivate my profile please.\n2. No, I want to see my matches.",
            'Русский': f"Так ты не узнаешь, что кому-то нравишься... Точно хочешь отключить свою анкету?\n\n\n1. Да, отключить анкету.\n2. Нет, вернуться назад.",
            'Українська': f"Так ти не дізнаєшся, що комусь подобаєшся... Точно хочеш відключити свою анкету?\n\n\n1. Так, відключити анкету..\n2. Ні, повернутись назад."
        }
        freeze_profile_message = freeze_profile_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(freeze_profile_message,
                                        reply_markup=show_n_not_show_markup)
        return DEACTIVE
    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "/language":
        await context.bot.send_message(user_id, 'Please select your language:', reply_markup=language_choice_markup)
        return LANGUAGE
    elif context.user_data.get(context.user_data.get('user_id'),update.message.text) == "/report":
        no_report_here_messages = {
            'Türkçe': f"Sadece profiller şikayet edeblirsiniz.",
            'English': f"Works only on someone's profile",
            'Русский': f"Жалобу можно оставить только при просмотре анкеты",
            'Українська': f"Скаргу можна залишити тільки підчас перегляду анкет"
        }
        no_report_here_message = no_report_here_messages.get(lang.get(user_id, 0),
                                                             f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(no_report_here_message)
    else:
        wrong_value_messages = {
            'Türkçe': f"Yanlış bir değer girdiniz!",
            'English': f"You entered an incorrect value!",
            'Русский': f"Вы ввели неправильное значение!",
            'Українська': f"Ви ввели неправильне значення!"
        }
        wrong_value_message = wrong_value_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(wrong_value_message,reply_markup=wait_menu_markup)
        return WAIT_MENU_EXE

user_last_len = {}

async def matching(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    last_mes = context.user_data.get(context.user_data.get('user_id'), update.message.text)
    if is_spam(update.effective_user.id):
        await update.message.reply_text("Çok hızlı mesaj gönderiyorsunuz. Geçici olarak engellendiniz.")
        return MATCHING
    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "/language":
        await context.bot.send_message(update.effective_user.id, 'Please select your language:',
                                       reply_markup=language_choice_markup)
        return LANGUAGE
    else:
        current_jobs = context.job_queue.get_jobs_by_name(name="dgc")
        for job in current_jobs:
            job.schedule_removal()
        async def check_who_likes(context: CallbackContext):
            try:
                conn = connection_pool.get_connection()
                cursor = conn.cursor()
                user_id = update.effective_user.id
                cursor.execute("SELECT LikeUserID FROM Likes WHERE LikedUserID = %s", (user_id,))
                likes = cursor.fetchall()
                cursor.close()
                conn.close()
                len_likes = len(likes)
                last_len = user_last_len.get(user_id, 0)
                if len_likes > 0 and last_len != len_likes:
                    user_last_len[user_id] = len_likes
                    someone_liked_messages = {
                        'Türkçe': f"{len_likes} kişi sizi beğendi.Bakmak istermisin?\n\n\n1. Göster.\n2. Artık aramıyorum.",
                        'English': f"{len_likes} person liked you. Have a look?\n\n\n1. Show.\n2. Not searching anymore.",
                        'Русский': f"Ты понравился {len_likes} человеку\n\n\n1. Показать.\n2. Не хочу больше никого смотреть.",
                        'Українська': f"Ти сподобався {len_likes} людині\n\n\n1. Показати.\n2. Не хочу більше нікого дивитися."
                    }
                    show_who_likes_markup = show_who_likes_choice.get(lang.get(user_id, 0))
                    show_who_likes_markup = ReplyKeyboardMarkup([show_who_likes_markup], resize_keyboard=True,one_time_keyboard=True)
                    someone_liked_message = someone_liked_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
                    await update.message.reply_text(someone_liked_message,reply_markup=show_who_likes_markup)
                    context.job.data = True
            except Exception as e:
                pass
            finally:
                await asyncio.sleep(1)
        job = context.job_queue.run_repeating(check_who_likes, interval=10, first=0, data=None,name="dgc")
        await job.run(context.application)
        user_id = context.user_data.get('user_id')
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT LikeUserID FROM Likes WHERE LikedUserID = %s", (user_id,))
        likes = cursor.fetchall()
        cursor.close()
        conn.close()
        len_likes = len(likes)
        if len_likes>0:
            current_jobs = context.job_queue.get_jobs_by_name(name="dgc")
            for job in current_jobs:
                job.schedule_removal()
            if context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Göster." or context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Show." or context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Показать." or context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Показати.":
                conn = connection_pool.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT PersonID, UserName, Age, Bio, Photo FROM Users JOIN Likes ON PersonID = LikeUserID WHERE LikedUserID = %s",
                    (user_id,))
                liked_users = cursor.fetchall()[0]
                userid, user_name, user_age, user_bio, user_photo = liked_users
                cursor.close()
                conn.close()
                conn = connection_pool.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT MesToPerson FROM Likes WHERE LikeUserID = %s AND LikedUserID = %s",
                    (userid, user_id))
                mes_to_person_result = cursor.fetchone()
                mes_to_person = mes_to_person_result[0]
                cursor.close()
                conn.close()
                if mes_to_person is not None and mes_to_person != 'None':
                    message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}\n\n\n Bu kişinin size bir mesajı var:\n {mes_to_person}"
                    await update.message.reply_photo(user_photo, caption=message_text, reply_markup=like_or_not_markup)
                    return SHOW_WHO_LIKES
                else:
                    message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}"
                    await update.message.reply_photo(user_photo, caption=message_text, reply_markup=like_or_not_markup)
                    return SHOW_WHO_LIKES

            elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Artık aramıyorum." or context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Not searching anymore." or context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Не хочу больше никого смотреть." or context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Не хочу більше нікого дивитися.":
                freeze_profile_messages = {
                    'Türkçe': f"Hesabınızı dondurmak istiyormusnuz?\n\n\n1. Evet\n2. Geri dön",
                    'English': f"You won't know who likes you then... Sure about deactivating?\n\n\n1. Yes, deactivate my profile please.\n2. No, I want to see my matches.",
                    'Русский': f"Так ты не узнаешь, что кому-то нравишься... Точно хочешь отключить свою анкету?\n\n\n1. Да, отключить анкету.\n2. Нет, вернуться назад.",
                    'Українська': f"Так ти не дізнаєшся, що комусь подобаєшся... Точно хочеш відключити свою анкету?\n\n\n1. Так, відключити анкету..\n2. Ні, повернутись назад."
                }
                freeze_profile_message = freeze_profile_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
                await update.message.reply_text(freeze_profile_message,reply_markup=show_n_not_show_markup)
                user_last_len[user_id] = 0
                return DEACTIVE
        else:
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DailyViewCount FROM Users WHERE PersonID = %s", (user_id,))
            view_count = cursor.fetchone()
            cursor.close()
            conn.close()
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Premium FROM Users WHERE PersonID = %s", (context.user_data.get('user_id'),))
            user_premium_status = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            if view_count and view_count[0] > 0 or user_premium_status > 0:
                try:
                    liked_user_id = context.user_data.get('liked_user_id')
                    conn = connection_pool.get_connection()
                    cursor = conn.cursor()
                    user_id = context.user_data.get('user_id')
                    cursor.execute("SELECT UserName, Age, Bio, Photo FROM Users WHERE PersonID = %s", (user_id,))
                    result = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    user_name, user_age, user_bio, user_photo = result
                    last_mes = context.user_data.get(context.user_data.get('user_id'), update.message.text)
                    if context.user_data.get(context.user_data.get('user_id'), update.message.text) == "❤️":
                        message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}"
                        conn = connection_pool.get_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM Likes WHERE LikeUserID = %s AND LikedUserID = %s", (user_id, liked_user_id))
                        existing_like = cursor.fetchone()
                        cursor.close()
                        conn.close()
                        if existing_like:
                            pass
                        else:
                            conn = connection_pool.get_connection()
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO Likes (LikeUserID, LikedUserID) VALUES (%s, %s)", (user_id, liked_user_id))
                            cursor.close()
                            conn.close()
                    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "💌" and context.user_data.get('flag_user') != None:
                        mes_person_id = liked_user_id
                        context.user_data['mes_person_id'] = mes_person_id
                        return SAVE_MESSAGE
                    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "👎":
                        pass
                    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "💤":
                        return WAIT_MENU_EXE
                    elif last_mes == "/language":
                        await context.bot.send_message(user_id, 'Please select your language:',
                                                       reply_markup=language_choice_markup)
                        return LANGUAGE
                    elif last_mes == "/report" and context.user_data.get('flag_user') != None:
                        return REPORT_USER
                    elif last_mes == "Evet" or last_mes == "Yes" or last_mes == "Да" or last_mes == "Так":
                        pass
                    elif last_mes == "Geri dön" or last_mes == "Go back" or last_mes == "вернуться назад" or last_mes == "Повернутися назад":
                        conn = connection_pool.get_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT UserName, Age, Bio, Photo, Premium FROM Users WHERE PersonID = %s",
                                       (user_id,))
                        result = cursor.fetchone()
                        user_name, user_age, user_bio, user_photo, user_premium = result
                        cursor.close()
                        conn.close()
                        message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}  {"| Premium ❤️‍🔥 " if user_premium > 0 else ''}"
                        your_profile_messages = {
                            'Türkçe': f"Profiliniz:",
                            'English': f"Your profile:",
                            'Русский': f"Так выглядит твоя анкета:",
                            'Українська': f"Так виглядає твоя анкета:"
                        }
                        your_profile_message = your_profile_messages.get(lang.get(user_id, 0),
                                                                         f"Unsupported language: {lang.get(user_id, 0)}")
                        await update.message.reply_text(your_profile_message)
                        await update.message.reply_photo(f"{user_photo if user_photo is not None else 'None'}",
                                                         caption=message_text)
                        profile_messages = {
                            'Türkçe': f"1. Profilimi Düzenle.\n"
                                      f"2. Profil fotoğrafımı değiştir.\n"
                                      f"3. Biografimi düzenle.\n"
                                      f"4. Profilleri Görmeye Başla.",
                            'English': f"1. Edit My Profile.\n"
                                       f"2. Change My Profile Picture.\n"
                                       f"3. Edit My Bio.\n"
                                       f"4. Start Viewing Profiles.",
                            'Русский': f"1. Заполнить анкету заново. \n"
                                       f"2. Изменить фото.\n"
                                       f"3. Изменить текст анкеты.\n"
                                       f"4. Смотреть анкеты.",
                            'Українська': f"1. Заповнити анкету наново.\n"
                                          f"2. Змінити фото. \n"
                                          f"3. Змінити текст анкети.\n"
                                          f"4. Дивитися анкети."
                        }
                        profile_message = profile_messages.get(lang.get(user_id, 0),
                                                               f"Unsupported language: {lang.get(user_id, 0)}")
                        await update.message.reply_text(profile_message, reply_markup=menu_markup)

                        return MENU_EXE
                    else:
                        no_option_messages = {
                            'Türkçe': f"Böyle bir seçenek yok",
                            'English': f"There is no such option.",
                            'Русский': f"Такого варианта нет.",
                            'Українська': f"Такої опції немає."
                        }
                        no_option_message = no_option_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
                        await update.message.reply_text(no_option_message,reply_markup=like_markup)
                        return MATCHING

                    conn = connection_pool.get_connection()
                    cursor = conn.cursor()
                    user_id = context.user_data.get('user_id')
                    cursor.execute("SELECT Looking, Gender FROM Users WHERE PersonID = %s", (user_id,))
                    looking, user_gender = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    if looking == "Kızlar" and user_gender == "Erkek":
                        user_looking = "Erkekler"
                        match_gender = "Kız"
                    elif looking == "Erkekler" and user_gender == "Kız":
                        user_looking = "Kızlar"
                        match_gender = "Erkek"
                    elif looking == "Kızlar" and user_gender == "Kız":
                        user_looking = "Kızlar"
                        match_gender = "Kız"
                    elif looking == "Erkekler" and user_gender == "Erkek":
                        user_looking = "Erkekler"
                        match_gender = "Erkek"
                    else:
                        user_looking = "Kızlar"
                        user_gender = "Erkek"
                    conn = connection_pool.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT Age FROM Users WHERE PersonID = %s AND Bio IS NOT NULL AND Photo IS NOT NULL", (context.user_data.get('user_id'),))
                    my_user_age = cursor.fetchone()[0]
                    cursor.close()
                    conn.close()
                    conn = connection_pool.get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT COUNT(*) FROM Users WHERE Gender = %s AND Looking = %s AND IsActive = 1 AND PersonID NOT IN (SELECT LikedUserID FROM Likes WHERE LikeUserID = %s) AND Age BETWEEN %s AND %s AND PersonID != %s AND Bio IS NOT NULL AND Photo IS NOT NULL",
                        (match_gender, user_looking, user_id, my_user_age - 5, my_user_age + 5,user_id)
                    )
                    total_users = cursor.fetchone()[0]
                    cursor.close()
                    conn.close()
                    if total_users == None or total_users == "None" or total_users == 0:
                        limit_messages = {
                            'Türkçe': f"Kriterlerinize uygun birini şu anda bulamadım. Lütfen bir süre sonra gelip tekrar deneyin.☺",
                            'English': f"Unable to find someone that meets your criteria at the moment. Please come back later and try again.☺",
                            'Русский': f"На данный момент не удается найти подходящего человека. Пожалуйста, вернитесь позже и попробуйте снова.☺",
                            'Українська': f"Наразі не вдається знайти відповідну особу. Будь ласка, поверніться пізніше і спробуйте знову.☺"
                        }
                        limit_message = limit_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
                        go_back_text_markup = go_back_text.get(lang.get(user_id, 0))
                        go_back_text_markup = ReplyKeyboardMarkup([go_back_text_markup], resize_keyboard=True,
                                                                  one_time_keyboard=True)
                        await update.message.reply_text(limit_message,reply_markup=go_back_text_markup)
                        return SHOW_PROFILE
                    random_index = random.randint(0, total_users - 1)
                    conn = connection_pool.get_connection()
                    cursor = conn.cursor()
                    sql_query = (
                        "SELECT PersonID, UserName, Age, Bio, Photo FROM Users WHERE Gender = %s AND Looking = %s AND IsActive = 1 AND PersonID NOT IN (SELECT LikedUserID FROM Likes WHERE LikeUserID = %s) AND Age BETWEEN %s AND %s AND Bio IS NOT NULL AND Photo IS NOT NULL LIMIT 1 OFFSET %s"
                    )
                    cursor.execute(sql_query,
                                   (match_gender, user_looking, user_id, my_user_age - 5, my_user_age + 5, random_index))
                    random_user = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    userid, user_name, user_age, user_bio, user_photo = random_user
                    liked_user_id = userid
                    context.user_data['liked_user_id'] = liked_user_id
                    flag_user = userid
                    context.user_data['flag_user'] = flag_user
                    message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}"
                    await update.message.reply_photo(user_photo, caption=message_text, reply_markup=like_markup)
                except Exception as e:
                    print(e)
                    pass
                finally:
                    conn = connection_pool.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT Premium FROM Users WHERE PersonID = %s",
                                   (user_id,))
                    result = cursor.fetchone()
                    user_premium = result[0] if result else 0
                    cursor.close()
                    conn.close()
                    if int(user_premium) > 0:
                        pass
                    else:
                        conn = connection_pool.get_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE Users SET DailyViewCount = DailyViewCount - 1 WHERE PersonID = %s",(user_id,))
                        cursor.close()
                        conn.close()
                    if context.user_data.get(context.user_data.get('user_id'), update.message.text) == "💤":
                        wait_message_messages = {
                            'Türkçe': f"Biri sizi görene kadar bekleyin.",
                            'English': f"Wait until someone sees you.",
                            'Русский': f"Подождем пока кто-то увидит твою анкету",
                            'Українська': f"Почекаємо поки хтось побачить твою анкету",
                        }
                        wait_exe_messages = {
                            'Türkçe': f"1.Profilleri Görmeye başla.\n"
                                      f"2.Profilim.\n"
                                      f"3.Artık aramıyorum.\n",
                            'English': f"1.View profiles.\n"
                                      f"2.My profile.\n"
                                      f"3.Not searching anymore.\n",
                            'Русский': f"1.Смотреть анкеты.\n"
                                       f"2.Моя анкета.\n"
                                       f"3.Я больше не хочу никого искать.\n",
                            'Українська': f"1.Дивитися анкети.\n"
                                       f"2.Моя анкета.\n"
                                       f"3.Я більше не хочу нікого шукати.\n",
                        }
                        wait_exe_message = wait_exe_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
                        wait_message_message = wait_message_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
                        await update.message.reply_text(wait_message_message)
                        await update.message.reply_text(wait_exe_message, reply_markup=wait_menu_markup)
                        return WAIT_MENU_EXE
                    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "💌" and context.user_data.get('flag_user') != None:
                        flag_user = None
                        context.user_data['flag_user'] = flag_user
                        write_message_messages = {
                            'Türkçe': f"Göndermek istediğiniz mesajı yazın...",
                            'English': f"Write a message for this user",
                            'Русский': f"Напиши сообщение для этого пользователя",
                            'Українська': f"Напиши повідомлення для цього користувача",
                        }
                        write_message_message = write_message_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
                        go_back_text_markup = go_back_text.get(lang.get(user_id, 0))
                        go_back_text_markup = ReplyKeyboardMarkup([go_back_text_markup], resize_keyboard=True,
                                                                  one_time_keyboard=True)
                        await update.message.reply_text(write_message_message,reply_markup=go_back_text_markup)
                        return SAVE_MESSAGE
                    elif context.user_data.get(context.user_data.get('user_id'),update.message.text) == "/report" and context.user_data.get('flag_user') != None:
                        flag_user = None
                        context.user_data['flag_user'] = flag_user
                        rep_person_id = context.user_data.get('liked_user_id')
                        context.user_data['rep_person_id'] = rep_person_id
                        report_user_messages = {
                            'Türkçe': f"Sebebini belirtin.\n\n"
                                      f"1. 🔞 Cinsellik materyali.\n"
                                      f"2. 💊 Uyuşturucu ticareti.\n"
                                      f"3. 💰 Mal ve hizmet satışı\n"
                                      f"4. 🦨 Diğeri.\n"
                                      f"***\n"
                                      f"9.Geri dön.",
                            'English': f"Specify the reason.\n\n"
                                       f"1. 🔞 Adult material.\n"
                                       f"2. 💊 Drug propaganda.\n"
                                       f"3. 💰 Sale of goods and services.\n"
                                       f"4. 🦨 Others.\n"
                                       f"***\n"
                                       f"9. Go back.",
                            'Русский': f"Укажите причину жалобы\n\n"
                                       f"1. 🔞 Материал для взрослых.\n"
                                       f"2. 💊 Пропаганда наркотиков.\n"
                                       f"3. 💰 Продажа товаров и услуг.\n"
                                       f"4. 🦨 Другое.\n"
                                       f"***\n"
                                       f"9.Вернуться назад.",
                            'Українська': f"Вкажіть причину скарги\n\n"
                                          f"1. 🔞 Матеріал для дорослих.\n"
                                          f"2. 💊 Drug propaganda.\n"
                                          f"3. 💰 Продаж товарів і послуг.\n"
                                          f"4. 🦨 Інше.\n"
                                          f"***\n"
                                          f"9. Повернутись назад.",
                        }
                        report_user_message = report_user_messages.get(lang.get(user_id, 0),
                                                                       f"Unsupported language: {lang.get(user_id, 0)}")
                        await context.bot.send_message(user_id, report_user_message, reply_markup=report_markup)
                        return REPORT_USER
                    elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "Geri dön":
                        return MENU_EXE
                    else:
                        return MATCHING
            else:
                daily_like_messages = {
                    'Türkçe': f"Günlük beğenme limitine ulaştınız 24 saat sonra tekrar gelin",
                    'English': f"You have reached the daily liking limit. Please come back in 24 hours.",
                    'Русский': f"Вы достигли суточного лимита лайков. Пожалуйста, вернитесь через 24 часа.",
                    'Українська': f"Ви досягли щоденного ліміту лайків. Будь ласка, поверніться через 24 години."
                }
                daily_like_message = daily_like_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
                go_back_text_markup = go_back_text.get(lang.get(user_id, 0))
                go_back_text_markup = ReplyKeyboardMarkup([go_back_text_markup], resize_keyboard=True,one_time_keyboard=True)
                await update.message.reply_text(daily_like_message,reply_markup=go_back_text_markup)
                return SHOW_PROFILE

async def save_the_message(update: Update, context: CallbackContext):
    mes_person_id = context.user_data.get('mes_person_id')
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    yes_markup = yes_text.get(lang.get(user_id, 0))
    yes_markup = ReplyKeyboardMarkup([yes_markup], resize_keyboard=True, one_time_keyboard=True)
    last_mes = context.user_data.get(context.user_data.get('user_id'), update.message.text)
    if last_mes == "Geri dön" or last_mes == "Go back" or last_mes == "вернуться назад" or last_mes == "Повернутися назад":
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT PersonID,UserName, Age, Bio, Photo FROM Users WHERE PersonID = %s", (mes_person_id,))
        mes_user = cursor.fetchone()
        cursor.close()
        conn.close()
        userid, user_name, user_age, user_bio, user_photo = mes_user
        message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}"
        await update.message.reply_photo(user_photo, caption=message_text, reply_markup=like_markup)

        return MATCHING
    else:
        mes_to_person = context.user_data.get(context.user_data.get('user_id'), update.message.text)
        if mes_to_person == 'None' or mes_to_person == None:
            user_id = context.user_data.get('user_id')
            incorrect_value_messages = {
                'Türkçe': f"Geçersiz bir değer girdiniz!",
                'English': f"You entered an incorrect value!",
                'Русский': f"Вы ввели неправильное значение!",
                'Українська': f"Ви ввели неправильне значення!"
            }
            incorrect_value_message = incorrect_value_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(incorrect_value_message)
            return SAVE_MESSAGE
        user_id = context.user_data.get('user_id')

        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Likes (LikeUserID, LikedUserID,MesToPerson) VALUES (%s, %s,%s)",
                       (user_id, mes_person_id, mes_to_person))
        cursor.close()
        conn.close()
        con_profile_messages = {
            'Türkçe': f"Profilleri Görmeye devam edelim mi? 🥰",
            'English': f"Shall we continue to view profiles? 🥰",
            'Русский': f"Давайте продолжим просмотр профилей? 🥰",
            'Українська': f"Чи хочете ми продовжимо перегляд профілів? 🥰"
        }
        con_profile_message = con_profile_messages.get(lang.get(user_id, 0),
                                                         f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(con_profile_message, reply_markup=yes_markup)
        return MATCHING
async def report_user(update: Update, context: CallbackContext):
    rep_person_id = context.user_data.get('rep_person_id')
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    yes_markup = yes_text.get(lang.get(user_id, 0))
    yes_markup = ReplyKeyboardMarkup([yes_markup], resize_keyboard=True, one_time_keyboard=True)
    last_mes = context.user_data.get(context.user_data.get('user_id'), update.message.text)
    if last_mes == "9":
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT PersonID,UserName, Age, Bio, Photo FROM Users WHERE PersonID = %s", (rep_person_id,))
        mes_user = cursor.fetchone()
        cursor.close()
        conn.close()
        userid, user_name, user_age, user_bio, user_photo = mes_user
        message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}"
        await update.message.reply_photo(user_photo, caption=message_text, reply_markup=like_markup)

        return MATCHING
    else:
        mes_to_person = context.user_data.get(context.user_data.get('user_id'), update.message.text)
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Reports WHERE UserID = %s", (rep_person_id,))
        row_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        if mes_to_person != '1🔞' and mes_to_person != '2💊' and mes_to_person != '3💰' and mes_to_person != '4🦨' and mes_to_person != '9':
            user_id = context.user_data.get('user_id')
            incorrect_value_messages = {
                'Türkçe': f"Geçersiz bir değer girdiniz!",
                'English': f"You entered an incorrect value!",
                'Русский': f"Вы ввели неправильное значение!",
                'Українська': f"Ви ввели неправильне значення!"
            }
            incorrect_value_message = incorrect_value_messages.get(lang.get(user_id, 0),f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(incorrect_value_message)
            return REPORT_USER
        elif mes_to_person == '1🔞':
            if row_count > 0:
                conn = connection_pool.get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE Reports SET AdultREP = AdultREP + 1 WHERE UserID = %s", (rep_person_id,))
                cursor.close()
                conn.close()
            else:
                conn = connection_pool.get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Reports (UserID, AdultREP) VALUES (%s, 1)", (rep_person_id,))
                cursor.close()
                conn.close()
            con_profile_messages = {
                'Türkçe': f"Profilleri Görmeye devam edelim mi? 🥰",
                'English': f"Shall we continue to view profiles? 🥰",
                'Русский': f"Давайте продолжим просмотр профилей? 🥰",
                'Українська': f"Чи хочете ми продовжимо перегляд профілів? 🥰"
            }
            con_profile_message = con_profile_messages.get(lang.get(user_id, 0),
                                                             f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(con_profile_message, reply_markup=yes_markup)
            return MATCHING
        elif mes_to_person == '2💊':
            if row_count > 0:
                conn = connection_pool.get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE Reports SET DrugREP = DrugREP + 1 WHERE UserID = %s", (rep_person_id,))
                cursor.close()
                conn.close()
                con_profile_messages = {
                    'Türkçe': f"Profilleri Görmeye devam edelim mi? 🥰",
                    'English': f"Shall we continue to view profiles? 🥰",
                    'Русский': f"Давайте продолжим просмотр профилей? 🥰",
                    'Українська': f"Чи хочете ми продовжимо перегляд профілів? 🥰"
                }
                con_profile_message = con_profile_messages.get(lang.get(user_id, 0),
                                                               f"Unsupported language: {lang.get(user_id, 0)}")
                await update.message.reply_text(con_profile_message, reply_markup=yes_markup)
                return MATCHING
            else:
                conn = connection_pool.get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Reports (UserID, DrugREP) VALUES (%s, 1)", (rep_person_id,))
                cursor.close()
                conn.close()
            con_profile_messages = {
                'Türkçe': f"Profilleri Görmeye devam edelim mi? 🥰",
                'English': f"Shall we continue to view profiles? 🥰",
                'Русский': f"Давайте продолжим просмотр профилей? 🥰",
                'Українська': f"Чи хочете ми продовжимо перегляд профілів? 🥰"
            }
            con_profile_message = con_profile_messages.get(lang.get(user_id, 0),
                                                             f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(con_profile_message, reply_markup=yes_markup)
            return MATCHING
        elif mes_to_person == '3💰':
            if row_count > 0:
                conn = connection_pool.get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE Reports SET SaleREP = SaleREP + 1 WHERE UserID = %s", (rep_person_id,))
                cursor.close()
                conn.close()
                con_profile_messages = {
                    'Türkçe': f"Profilleri Görmeye devam edelim mi? 🥰",
                    'English': f"Shall we continue to view profiles? 🥰",
                    'Русский': f"Давайте продолжим просмотр профилей? 🥰",
                    'Українська': f"Чи хочете ми продовжимо перегляд профілів? 🥰"
                }
                con_profile_message = con_profile_messages.get(lang.get(user_id, 0),
                                                               f"Unsupported language: {lang.get(user_id, 0)}")
                await update.message.reply_text(con_profile_message, reply_markup=yes_markup)
                return MATCHING
            else:
                conn = connection_pool.get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Reports (UserID, SaleREP) VALUES (%s, 1)", (rep_person_id,))
                cursor.close()
                conn.close()
            con_profile_messages = {
                'Türkçe': f"Profilleri Görmeye devam edelim mi? 🥰",
                'English': f"Shall we continue to view profiles? 🥰",
                'Русский': f"Давайте продолжим просмотр профилей? 🥰",
                'Українська': f"Чи хочете ми продовжимо перегляд профілів? 🥰"
            }
            con_profile_message = con_profile_messages.get(lang.get(user_id, 0),
                                                             f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(con_profile_message, reply_markup=yes_markup)
            return MATCHING
        elif mes_to_person == '4🦨':
            if row_count > 0:
                conn = connection_pool.get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE Reports SET OtherREP = OtherREP + 1 WHERE UserID = %s", (rep_person_id,))
                cursor.close()
                conn.close()
                con_profile_messages = {
                    'Türkçe': f"Profilleri Görmeye devam edelim mi? 🥰",
                    'English': f"Shall we continue to view profiles? 🥰",
                    'Русский': f"Давайте продолжим просмотр профилей? 🥰",
                    'Українська': f"Чи хочете ми продовжимо перегляд профілів? 🥰"
                }
                con_profile_message = con_profile_messages.get(lang.get(user_id, 0),
                                                               f"Unsupported language: {lang.get(user_id, 0)}")
                await update.message.reply_text(con_profile_message, reply_markup=yes_markup)
                return MATCHING
            else:
                conn = connection_pool.get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Reports (UserID, OtherREP) VALUES (%s, 1)", (rep_person_id,))
                cursor.close()
                conn.close()
            con_profile_messages = {
                'Türkçe': f"Profilleri Görmeye devam edelim mi? 🥰",
                'English': f"Shall we continue to view profiles? 🥰",
                'Русский': f"Давайте продолжим просмотр профилей? 🥰",
                'Українська': f"Чи хочете ми продовжимо перегляд профілів? 🥰"
            }
            con_profile_message = con_profile_messages.get(lang.get(user_id, 0),
                                                             f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(con_profile_message, reply_markup=yes_markup)
            return MATCHING
        elif mes_to_person == '9':
            con_profile_messages = {
                'Türkçe': f"Profilleri Görmeye devam edelim mi? 🥰",
                'English': f"Shall we continue to view profiles? 🥰",
                'Русский': f"Давайте продолжим просмотр профилей? 🥰",
                'Українська': f"Чи хочете ми продовжимо перегляд профілів? 🥰"
            }
            con_profile_message = con_profile_messages.get(lang.get(user_id, 0),
                                                             f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(con_profile_message, reply_markup=yes_markup)
            return MATCHING
async def de_active_or_not(update: Update, context: CallbackContext):
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    show_profiles_markup = show_profiles.get(lang.get(user_id, 0))
    show_profiles_markup = ReplyKeyboardMarkup([show_profiles_markup], resize_keyboard=True, one_time_keyboard=True)
    if is_spam(update.effective_user.id):
        await update.message.reply_text("Çok hızlı mesaj gönderiyorsunuz. Geçici olarak engellendiniz.")
        return DEACTIVE
    else:
        user_id = context.user_data.get('user_id')
        if context.user_data.get(context.user_data.get('user_id'), update.message.text) == "1":
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET IsActive = 0 WHERE PersonID = %s", (user_id,))
            cursor.close()
            conn.close()
            end_messages = {
                'Türkçe': f"Umarım benim yardımımla biriyle tanışmışsınızdır!\nSohbet etmekten her zaman mutluluk duyarım. Sıkılırsanız bana mesaj atın - sizin için özel birini bulacağım.\n1. Profilleri görüntüle",
                'English': f"Hope you met someone with my help!\nAlways happy to chat. If bored, text me -  I'll find someone special for you.\n1. View profiles",
                'Русский': f"Надеюсь ты нашел кого-то благодаря мне!\nРад был с тобой пообщаться, будет скучно – пиши, обязательно найдем тебе кого-нибудь\n1. Смотреть анкеты",
                'Українська': f"Сподіваюсь ти когось знайшов з моєю допомогою!\nРадий був поспілкуватися, якщо буде нудно – пиши, обов'язково знайдем тобі когось\n1. Дивитися анкети"
            }
            end_message = end_messages.get(lang.get(user_id, 0),
                                                             f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(end_message,reply_markup=show_profiles_markup)
            return NONEACTIVE
        elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "2":
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT UserName, Age, Bio, Photo, Premium FROM Users WHERE PersonID = %s", (user_id,))
            result = cursor.fetchone()
            user_name, user_age, user_bio, user_photo, user_premium = result
            cursor.close()
            conn.close()
            message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}, |{" Premium ❤️‍🔥 " if user_premium > 0 else ''}"
            your_profile_messages = {
                'Türkçe': f"Profiliniz:",
                'English': f"Your profile:",
                'Русский': f"Так выглядит твоя анкета:",
                'Українська': f"Так виглядає твоя анкета:"
            }
            your_profile_message = your_profile_messages.get(lang.get(user_id, 0),
                                                             f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(your_profile_message)
            await update.message.reply_photo(f"{user_photo if user_photo is not None else 'None'}",
                                             caption=message_text)
            profile_messages = {
                'Türkçe': f"1. Profilimi Düzenle.\n"
                          f"2. Profil fotoğrafımı değiştir.\n"
                          f"3. Biografimi düzenle.\n"
                          f"4. Profilleri Görmeye Başla.",
                'English': f"1. Edit My Profile.\n"
                           f"2. Change My Profile Picture.\n"
                           f"3. Edit My Bio.\n"
                           f"4. Start Viewing Profiles.",
                'Русский': f"1. Заполнить анкету заново. \n"
                           f"2. Изменить фото.\n"
                           f"3. Изменить текст анкеты.\n"
                           f"4. Смотреть анкеты.",
                'Українська': f"1. Заповнити анкету наново.\n"
                              f"2. Змінити фото. \n"
                              f"3. Змінити текст анкети.\n"
                              f"4. Дивитися анкети."
            }
            profile_message = profile_messages.get(lang.get(user_id, 0),
                                                   f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(profile_message, reply_markup=menu_markup)

            return MENU_EXE
        else:
            wrong_value_messages = {
                'Türkçe': f"Yanlış bir değer girdiniz!",
                'English': f"You entered an incorrect value!",
                'Русский': f"Вы ввели неправильное значение!",
                'Українська': f"Ви ввели неправильне значення!"
            }
            wrong_value_message = wrong_value_messages.get(lang.get(user_id, 0),
                                                             f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(wrong_value_message,reply_markup=show_n_not_show_markup)
            return DEACTIVE


async def not_active(update: Update, context: CallbackContext):
    if is_spam(update.effective_user.id):
        await update.message.reply_text("Çok hızlı mesaj gönderiyorsunuz. Geçici olarak engellendiniz.")
        return NONEACTIVE
    else:
        user_id = context.user_data.get('user_id')
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
        ban = cursor.fetchone()
        cursor.close()
        conn.close()
        if ban:
            await context.bot.send_message(user_id, "You Are banned!")
            return BANNED
        last_mes = context.user_data.get(context.user_data.get('user_id'), update.message.text)
        if last_mes == "Profilleri görüntüle." or last_mes == "View profiles." or last_mes == "Смотреть анкеты." or last_mes == "Дивитися анкети.":
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET IsActive = 1 WHERE PersonID = %s", (user_id,))
            cursor.close()
            conn.close()
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT UserName, Age, Bio, Photo, Premium FROM Users WHERE PersonID = %s", (user_id,))
            result = cursor.fetchone()
            user_name, user_age, user_bio, user_photo, user_premium = result
            cursor.close()
            conn.close()
            message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}  {"| Premium ❤️‍🔥 " if user_premium > 0 else ''}"
            your_profile_messages = {
                'Türkçe': f"Profiliniz:",
                'English': f"Your profile:",
                'Русский': f"Так выглядит твоя анкета:",
                'Українська': f"Так виглядає твоя анкета:"
            }
            your_profile_message = your_profile_messages.get(lang.get(user_id, 0),
                                                             f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(your_profile_message)
            await update.message.reply_photo(f"{user_photo if user_photo is not None else 'None'}",
                                             caption=message_text)
            profile_messages = {
                'Türkçe': f"1. Profilimi Düzenle.\n"
                          f"2. Profil fotoğrafımı değiştir.\n"
                          f"3. Biografimi düzenle.\n"
                          f"4. Profilleri Görmeye Başla.",
                'English': f"1. Edit My Profile.\n"
                           f"2. Change My Profile Picture.\n"
                           f"3. Edit My Bio.\n"
                           f"4. Start Viewing Profiles.",
                'Русский': f"1. Заполнить анкету заново. \n"
                           f"2. Изменить фото.\n"
                           f"3. Изменить текст анкеты.\n"
                           f"4. Смотреть анкеты.",
                'Українська': f"1. Заповнити анкету наново.\n"
                              f"2. Змінити фото. \n"
                              f"3. Змінити текст анкети.\n"
                              f"4. Дивитися анкети."
            }
            profile_message = profile_messages.get(lang.get(user_id, 0),
                                                   f"Unsupported language: {lang.get(user_id, 0)}")
            await update.message.reply_text(profile_message, reply_markup=menu_markup)

            return MENU_EXE
        else:
            wrong_value_messages = {
                'Türkçe': f"Yanlış bir değer girdiniz!",
                'English': f"You entered an incorrect value!",
                'Русский': f"Вы ввели неправильное значение!",
                'Українська': f"Ви ввели неправильне значення!"
            }
            wrong_value_message = wrong_value_messages.get(lang.get(user_id, 0),
                                                           f"Unsupported language: {lang.get(user_id, 0)}")
            show_profiles_markup = show_profiles.get(lang.get(user_id, 0))
            show_profiles_markup = ReplyKeyboardMarkup([show_profiles_markup], resize_keyboard=True,
                                                       one_time_keyboard=True)
            await update.message.reply_text(wrong_value_message,reply_markup=show_profiles_markup)
            return NONEACTIVE

async def show_who_likes(update: Update, context: CallbackContext):
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned WHERE PersonID = %s", (user_id,))
    ban = cursor.fetchone()
    cursor.close()
    conn.close()
    if ban:
        await context.bot.send_message(user_id, "You Are banned!")
        return BANNED
    yes_markup = yes_text.get(lang.get(user_id, 0))
    yes_markup = ReplyKeyboardMarkup([yes_markup], resize_keyboard=True, one_time_keyboard=True)
    if is_spam(update.effective_user.id):
        await update.message.reply_text("Çok hızlı mesaj gönderiyorsunuz. Geçici olarak engellendiniz.")
        return SHOW_WHO_LIKES
    else:
        user_id = context.user_data.get('user_id')
        try:
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT LikeUserID FROM Likes WHERE LikedUserID = %s", (user_id,))
            likes = cursor.fetchall()
            cursor.close()
            conn.close()
            len_likes = len(likes)
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT PersonID, UserName, Age, Bio, Photo FROM Users JOIN Likes ON PersonID = LikeUserID WHERE LikedUserID = %s",
                (user_id,))
            liked_users = cursor.fetchall()[0]
            cursor.close()
            conn.close()
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT PersonID,UserName, Age, Bio, Photo FROM Users WHERE PersonID = %s",
                           (user_id,))
            user_info = cursor.fetchone()
            cursor.close()
            conn.close()
            my_userid, my_user_name, my_user_age, my_user_bio, my_user_photo = user_info
            personid, user_name, user_age, user_bio, user_photo = liked_users
            message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}"
            my_user_message_text = f"{my_user_name}, {my_user_age}, {my_user_bio if my_user_bio is not None else 'None'}"
            if context.user_data.get(context.user_data.get('user_id'), update.message.text) == "❤️":
                await context.bot.send_photo(chat_id=user_id, photo=user_photo, caption=message_text)
                match_messages = {
                    'Türkçe': f"Harika! Umarım güzel vakit geçirirsiniz ;)\n\nSohbete başla 👉 <a href='tg://user?id={personid}'>{user_name}</a>",
                    'English': f"Excellent! Hope you'll have a good time ;)\n\nStart chatting 👉 <a href='tg://user?id={personid}'>{user_name}</a>",
                    'Русский': f"Отлично! Надеюсь, у вас будет хорошее время ;)\n\nНачните общение 👉 <a href='tg://user?id={personid}'>{user_name}</a>",
                    'Українська': f"Відмінно! Сподіваюся, вам буде весело ;)\n\nПочніть розмову 👉 <a href='tg://user?id={personid}'>{user_name}</a>"
                }
                match_message = match_messages.get(lang.get(user_id, 0),
                                                               f"Unsupported language: {lang.get(user_id, 0)}")
                await update.message.reply_text(match_message,parse_mode='HTML')
                await context.bot.send_photo(chat_id=personid, photo=my_user_photo, caption=my_user_message_text)
                user_match_messages = {
                    'Türkçe': f"Harika! Umarım güzel vakit geçirirsiniz ;)\n\nSohbete başla 👉 <a href='tg://user?id={my_userid}'>{my_user_name}</a>",
                    'English': f"Excellent! Hope you'll have a good time ;)\n\nStart chatting 👉 <a href='tg://user?id={my_userid}'>{my_user_name}</a>",
                    'Русский': f"Отлично! Надеюсь хорошо проведете время ;)\n\n Начинай общаться👉<a href='tg://user?id={my_userid}'>{my_user_name}</a>",
                    'Українська': f"Чудово! Сподіваюся, добре проведете час ;)\n\n Починай спілкуватися👉<a href='tg://user?id={my_userid}'>{my_user_name}</a>"
                }
                user_match_message = user_match_messages.get(lang.get(personid, 0),f"Unsupported language: {lang.get(user_id, 0)}")
                await context.bot.send_message(chat_id=personid, text=user_match_message,parse_mode='HTML')
                conn = connection_pool.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Likes WHERE LikeUserID = %s AND LikedUserID = %s", (personid, user_id))
                cursor.execute("DELETE FROM Likes WHERE LikedUserID = %s AND LikeUserID = %s", (user_id, personid))
                cursor.close()
                conn.close()
                return SHOW_WHO_LIKES
            elif context.user_data.get(context.user_data.get('user_id'), update.message.text) == "👎":
                conn = connection_pool.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Likes WHERE LikeUserID = %s AND LikedUserID = %s", (personid, user_id))
                cursor.close()
                conn.close()
                return SHOW_WHO_LIKES
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT PersonID, UserName, Age, Bio, Photo FROM Users JOIN Likes ON PersonID = LikeUserID WHERE LikedUserID = %s", (user_id,))
            liked_users = cursor.fetchall()[0]
            cursor.close()
            conn.close()
            if len_likes == 0:
                return_messages = {
                    'Türkçe': f"Buraya kadar, geri dönmek istermisin?",
                    'English': f"That's all for now. Move on?",
                    'Русский': f"Продолжить просмотр анкет",
                    'Українська': f"Продовжити дивитися анкети"
                }
                return_message = return_messages.get(lang.get(user_id, 0),
                                                               f"Unsupported language: {lang.get(user_id, 0)}")

                await update.message.reply_text(return_message, reply_markup=yes_markup)
                return MATCHING
            userid, user_name, user_age, user_bio, user_photo = liked_users
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT MesToPerson FROM Likes WHERE LikeUserID = %s AND LikedUserID = %s",
                (userid, user_id))
            mes_to_person_result = cursor.fetchone()
            mes_to_person = mes_to_person_result[0]
            cursor.close()
            conn.close()
            if mes_to_person is not None and mes_to_person != 'None':
                message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}\n\n\n Bu kişinin size bir mesajı var:\n {mes_to_person}"
            else:
                message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'}"
            await update.message.reply_photo(user_photo, caption=message_text, reply_markup=like_or_not_markup)
        except Exception as e:
            pass
        finally:
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT LikeUserID FROM Likes WHERE LikedUserID = %s", (user_id,))
            likes = cursor.fetchall()
            len_likes = len(likes)
            cursor.close()
            conn.close()
            if len_likes == 0:
                return_messages = {
                    'Türkçe': f"Buraya kadar, geri dönmek istermisin?",
                    'English': f"That's all for now. Move on?",
                    'Русский': f"Продолжить просмотр анкет",
                    'Українська': f"Продовжити дивитися анкети"
                }
                return_message = return_messages.get(lang.get(user_id, 0),
                                                     f"Unsupported language: {lang.get(user_id, 0)}")
                await update.message.reply_text(return_message, reply_markup=yes_markup)
                return SHOW_PROFILE
            else:
                return SHOW_WHO_LIKES
async def premium_sale(update: Update, context: CallbackContext):
    if update.message.text == '1 Aylık' or update.message.text == '1 Month' or update.message.text == '1 месяц' or update.message.text == '1 місяць':
        price = '999'
    elif update.message.text == '6 Aylık' or update.message.text == '6 Months' or update.message.text == '6 месяцев' or update.message.text == '6 місяців':
        price = '3999'
    elif update.message.text == '1 Yıllık' or update.message.text == '1 Year' or update.message.text == '1 год' or update.message.text == '1 рік':
        price = '4999'
    elif update.message.text == "Geri dön" or update.message.text == "Go back" or update.message.text == "вернуться назад" or update.message.text == "Повернутися назад":
        user_id = context.user_data.get('user_id')
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserName, Age, Bio, Photo, Premium FROM Users WHERE PersonID = %s", (user_id,))
        result = cursor.fetchone()
        user_name, user_age, user_bio, user_photo, user_premium = result
        cursor.close()
        conn.close()
        message_text = f"{user_name}, {user_age}, {user_bio if user_bio is not None else 'None'} {"| Premium ❤️‍🔥 " if user_premium > 0 else ''}"
        your_profile_messages = {
            'Türkçe': f"Profiliniz:",
            'English': f"Your profile:",
            'Русский': f"Так выглядит твоя анкета:",
            'Українська': f"Так виглядає твоя анкета:"
        }
        your_profile_message = your_profile_messages.get(lang.get(user_id, 0),
                                                         f"Unsupported language: {lang.get(user_id, 0)}")
        await update.message.reply_text(your_profile_message)
        await update.message.reply_photo(f"{user_photo if user_photo is not None else 'None'}", caption=message_text)
        profile_messages = {
            'Türkçe': f"1. Profilimi Düzenle.\n"
                      f"2. Profil fotoğrafımı değiştir.\n"
                      f"3. Biografimi düzenle.\n"
                      f"4. Profilleri Görmeye Başla.\n",
            'English': f"1. Edit My Profile.\n"
                       f"2. Change My Profile Picture.\n"
                       f"3. Edit My Bio.\n"
                       f"4. Start Viewing Profiles.",
            'Русский': f"1. Заполнить анкету заново. \n"
                       f"2. Изменить фото.\n"
                       f"3. Изменить текст анкеты.\n"
                       f"4. Смотреть анкеты.",
            'Українська': f"1. Заповнити анкету наново.\n"
                          f"2. Змінити фото. \n"
                          f"3. Змінити текст анкети.\n"
                          f"4. Дивитися анкети."
        }
        profile_message = profile_messages.get(lang.get(user_id, 0), f"Unsupported language: {lang.get(user_id, 0)}")
        await context.bot.send_message(user_id, profile_message, reply_markup=menu_markup)
        return MENU_EXE
    else:
        wrong_value_messages = {
            'Türkçe': f"Yanlış bir değer girdiniz!",
            'English': f"You entered an incorrect value!",
            'Русский': f"Вы ввели неправильное значение!",
            'Українська': f"Ви ввели неправильне значення!"
        }
        wrong_value_message = wrong_value_messages.get(lang.get(context.user_data.get('user_id'), 0),f"Unsupported language: {lang.get(context.user_data.get('user_id'), 0)}")
        user_id = update.effective_user.id
        pay_markup = pay_choice.get(lang.get(user_id, 0))
        pay_markup = ReplyKeyboardMarkup([pay_markup], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(wrong_value_message,reply_markup=pay_markup)
        return PREMIUM
    formatted_link = pay(user_id=context.user_data.get('user_id'),price=price)
    premium_999_messages = {
            'Türkçe': f"Satın alımı gerçekleştirmek için lütfen bağlantıyı takip edin \n\n 👉 <a href='{formatted_link}'>StanbulDatePremium 🛍</a>",
            'English': f"Please follow the link to make the purchase \n\n 👉 <a href='{formatted_link}'>StanbulDatePremium 🛍</a>",
            'Русский': f"Для совершения покупки перейдите по ссылке \n\n 👉<a href='{formatted_link}'>StanbulDatePremium 🛍</a>",
            'Українська': f"Для здійснення покупки перейдіть за посиланням \n\n 👉<a href='{formatted_link}'>StanbulDatePremium 🛍</a>"
        }
    premium_999_message = premium_999_messages.get(lang.get(context.user_data.get('user_id'), 0),f"Unsupported language: {lang.get(context.user_data.get('user_id'), 0)}")
    go_back_text_markup = go_back_text.get(lang.get(context.user_data.get('user_id'), 0))
    go_back_text_markup = ReplyKeyboardMarkup([go_back_text_markup], resize_keyboard=True,
                                              one_time_keyboard=True)
    await context.bot.send_message(chat_id=context.user_data.get('user_id'), text=premium_999_message, parse_mode='HTML',reply_markup=go_back_text_markup)
    return SHOW_PROFILE
async def banned_user(update:Update,context: CallbackContext):
    pass
async def language_control(context: CallbackContext):
    user_id = context.user_data.get('user_id')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Language FROM Users WHERE PersonID = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        lang[user_id] = result[0]
        context.user_data['lang'] = result[0]
    else:
        pass
def main():
    app = Application.builder().token(Token).build()
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(None, check_user_state),
            CommandHandler("start", start_command),
        ],
        states={
            CHECK_USER_STATE:[
                MessageHandler(None,
                                 check_user_state)
            ],
            LANGUAGE_COMMAND:[
                CommandHandler("language", language_command)
            ],
            LANGUAGE:[
                MessageHandler(None,
                                 language)
            ],
            NAME:[
                MessageHandler(filters.Regex("^(🇬🇧 English|🇹🇷 Türkçe|🇷🇺 Русский|🇺🇦 Українська)$"),
                               set_name
                               )

            ],
            AGE: [
                MessageHandler(None,
                               set_age
                               ),
            ],
            GENDER: [
                MessageHandler(None,
                               set_gender
                               ),
            ],
            LOOKING: [
                MessageHandler(filters.Regex("^(Erkek|Kız|Male|Female|Я парень|Я девушка|Я хлопець|Я дівчина|/language)$"),
                               set_looking
                               ),
            ],
            CITY: [
                MessageHandler(filters.Regex("^(Erkekler|Kızlar|Boys|Girls|Парни|Деушки|Хлопці|Дівчата|/language)$"),
                               set_city
                               ),
            ],
            BIO: [
                MessageHandler(filters.Regex("^(Avrupa Yakası|Istanbul Yakası|European side|Istanbul side|Европейская сторона|Стамбул Сиде|Європейська сторона|Стамбул Сіде|/language)$"),
                               set_bio
                               )
            ],
            CHANGEBIO: [
                MessageHandler(None,
                               change_bio
                               ),
            ],
            PHOTO: [
                MessageHandler(None,
                               set_photo
                               )
            ],
            SAVEPHOTO: [
                MessageHandler(None,
                               save_photo
                               )
            ],
            SAVE_MESSAGE: [
                MessageHandler(None,
                               save_the_message
                               ),
            ],
            SHOW_PROFILE: [
                MessageHandler(None,
                               show_profile
                               ),
            ],
            MENU_EXE: [
                MessageHandler(None,
                               menu_exe
                               ),
            ],
            WAIT_MENU_EXE: [
                MessageHandler(None,
                               wait_menu_exe
                               ),
            ],
            MATCHING: [
                MessageHandler(None,
                               matching
                               ),
            ],
            DEACTIVE: [
                MessageHandler(None,
                               de_active_or_not
                               ),
            ],
            NONEACTIVE: [
                MessageHandler(None,
                               not_active
                               ),
            ],
            SHOW_WHO_LIKES: [
                MessageHandler(None,
                               show_who_likes
                               ),
            ],
            REPORT_USER: [
                MessageHandler(None,
                               report_user
                               ),
            ],
            PREMIUM: [
                MessageHandler(None,
                               premium_sale
                               ),
            ],
            BANNED:[
                MessageHandler(None,
                               banned_user
                               ),
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("^Profilleri Görmeye başla$"), show_profile)],
        per_user=True
    )

    # Handlers
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("language",language_command))
    # Start the updater
    app.run_polling()


if __name__ == '__main__':
    main()
