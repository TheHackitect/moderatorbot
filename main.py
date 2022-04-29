# Moderator bot for Telegram group chat
# Created by THEHACKITECT 
# Github: https://github.com/thehackitect
# Website: https://thehackitect.herokuapp.com
#
# import modules
# https://api.telegram.org/bot1719159069:AAH145CVDF37nK3X2Ri1a5yhTAS8FB3UIZU/getme
#  https://api.telegram.org/1233125771/getme
import psycopg2
import logging
import time
import json
import re
from flask import Flask,render_template,send_from_directory
from sympy import per

# Telegram modukkes
from telegram import *
from telegram import update
from telegram.ext import *
from os import getenv as _


API_TOKEN = _("API_TOKEN")
CRYPT_ENC_KEY = _("CRYPT_ENC_KEY")
CRYPT_AUTH_TOKEN = _("CRYPT_AUTH_TOKEN")

#check configuration varoables

updater = Updater(API_TOKEN, use_context=True)
dispatcher = updater.dispatcher
bot = Bot(API_TOKEN)

# gives feedback should any error is encounterd
def bot_feedbacks(name,id,info):
    try:
        bot.send_message(chat_id='@thehackitect_feedbacks',text=f'{name} {id} {info}')
    except:
        pass

#connect to the database
try:
    mydb = psycopg2.connect(
    host=_("DB_HOST"),
    user=_("DB_USER"),
    password=_("DB_PASS"),
    database=_("DB_NAME"),
    port=_("DB_PORT")
    )
    mycursor = mydb.cursor()
except:
    bot_feedbacks("Bot_DB","ID","Unable to connect to Database!")

# To enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Developer keyboard
developer = [
            [
        InlineKeyboardButton(text='💬 Telwgram', url='https://t.me/thehackitect'),
        InlineKeyboardButton(text='💬 Twitter', url='https://twitter.com/thehackitect'),],
        [InlineKeyboardButton(text='👥 Github', url='https://github.com/thehackitect'),
        InlineKeyboardButton(text='👥 Channel', url='https://t.me/campusbots'),],
        [InlineKeyboardButton(text='🌎 Website', url='https://thehackitect.herokuapp.com'),]
        ]

markup_developer = InlineKeyboardMarkup(developer, one_time_keyboard=True)


# CONDITIONS TO USE BOT
def check_chat_type(update):
    chat_type = update.effective_chat.type
    if chat_type == "private":
        return  
    elif chat_type == "supergroup":
        return False
def check_db_connection(user_id):
    try:
        mycursor.execute("SELECT Maintenance FROM settings")
        maintenance = mycursor.fetchone()[0]
        return True
    except:
        mydb.rollback()
        return False
def force_join_group(user_id):
    in_group_status = (bot.get_chat_member(user_id = user_id, chat_id = "@campusbots")).status
    if in_group_status == "member" or in_group_status == "creator":
        return True
    else:
        return False
 

def check_if_user_exist(user_id):
    mycursor.execute(f"SELECT * FROM users_database WHERE ID = {user_id} ")
    myresult = mycursor.fetchone()
    if myresult == None:
        return False
    else:
        return True
        
        
def check_if_user_is_admin(user_id):
    try:
        mycursor.execute(f"SELECT * FROM admins WHERE ID = {user_id} ")
        adminresult = mycursor.fetchall()
        if not adminresult:
            return False
        else:
            return True
    except:
        return False


def check_maintenance_status(user_id):
    mycursor.execute("SELECT Maintenance FROM settings")
    maintenance = mycursor.fetchone()[0]
    if maintenance == "True":
        return True
    else:
        return False


def conditions(update: Update, the_id):        
    user_id = int(the_id)
    chat_type = check_chat_type(update)
    if chat_type == True:
        pass
    elif chat_type == False:
        update.message.reply_text(f"<a href='https://t.me/eksutelegrambot?start=eb'>🔗Click here to use EksuTelegrambot</a>",disable_web_page_preview =True,parse_mode = ParseMode.HTML,reply_markup=ReplyKeyboardRemove()) 
        return ConversationHandler.END
    connection_status = check_db_connection(user_id)
    in_group = force_join_group(user_id)
    user_exist = check_if_user_exist(user_id)
    admin_status = check_if_user_is_admin(user_id)
    maintenance_status = check_maintenance_status(user_id)

def load_settings(key):
    with open('settings.json') as data:
        info = json.load(data)
        text = info[key]
        return text

def new_group_mamber(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        group_id = update.message.chat_id
        group_name =update.effective_chat.title
        text = load_settings("welcome_message")
        message_id = (update.message.reply_text(f"Hi {member.full_name}!\n\nWelcome to <b>{group_name}</b>! <i>{text}</i>",disable_web_page_preview =True,parse_mode = ParseMode.HTML)).message_id 
        time.sleep(5)
        #bot.delete_message(chat_id=group_id,message_id=message_id)

# UNKNOWN
def unknown_commands(update, context):
    chat_type = update.effective_chat.type
    group_id = update.effective_chat.id
    try:
        replied_to_id = update.message.reply_to_message.from_user.id
    except:
        pass
    sender_id = update._effective_user.id
    sender_name = update._effective_user.first_name
    command = update.message.text
    status = (bot.get_chat_member(user_id = sender_id, chat_id = group_id)).status
    #bot.unban_chat_member(chat_id=group_id,user_id=sender_id)
    #bot.restrict_chat_member(chat_id=group_id,user_id=sender_id,permissions=ChatPermissions(can_send_messages=False))
    if chat_type =='private':
        context.bot.send_message(chat_id=update.effective_chat.id,text='❌ Unknown Command! \n reload the Menu by pressing /start')
        pass 
    elif chat_type =='supergroup':
        if status == "creator" or status == "administrator":
            try:
                if command == "/ban":
                    bot.ban_chat_member(chat_id=group_id,user_id=replied_to_id)
                elif command == "/unban":
                    bot.unban_chat_member(chat_id=group_id,user_id=replied_to_id)
                elif command == "/mute":
                    bot.restrict_chat_member(chat_id=group_id,user_id=replied_to_id,permissions=ChatPermissions(can_send_messages=False))
                elif command == "/unmute":
                    bot.restrict_chat_member(chat_id=group_id,user_id=replied_to_id,permissions=ChatPermissions(can_send_messages=True))
                #update.message.reply_text(f"Text here...",disable_web_page_preview =True,parse_mode = ParseMode.HTML,reply_markup=ReplyKeyboardRemove()) 
            except:
                pass
        else:
            pass



def unknown_texts(update, context):
    group_id = update.effective_chat.id
    sender_id = update._effective_user.id
    text = update.message.text
    chat_type = update.effective_chat.type
    status = (bot.get_chat_member(user_id = sender_id, chat_id = group_id)).status
    if chat_type =='private':
        context.bot.send_message(chat_id=update.effective_chat.id,text='Sorry i can not handle Dm messages for now! \n reload the Menu by pressing /start')
        pass 
    elif chat_type =='supergroup':
        text = update.message.text
        my_id = update.message.chat_id
        user_data = context.user_data
        x = update.effective_chat
        name = x.first_name
        '''
        handles unknown Texts sent to the group
        '''
        
        chat_type = update.effective_chat.type
        message_id = update.message.message_id
        if chat_type =='supergroup':
            group_name =update.effective_chat.title
            text = update.message.text.lower()
            text2 = update.message.text
            with open('settings.json') as setting:
                data = json.load(setting)
            #Checking for insults
            insult_tags = data["insult_tags"]
            questions_tags = data["question_tags"]
            possible_faq_tag = data["key_words"]
            greeting_tags = data["greeting_tags"]
            allowed_links = data["allowed_links"]
            for word in text.split():
                if word in insult_tags:
                    update.message.reply_text(f"Please do not use words like {word} in a group like this. thanks")
                    #Checking for questions
            for word in text.split():
                if word in questions_tags:
                    for i in possible_faq_tag:
                        if i in text.split():
                            reply = data[f"{i}"]
                            update.message.reply_text(reply,parse_mode = ParseMode.HTML)
                    #Checking for greeting       
            for word in text2.split():
                if word in greeting_tags: 
                    update.message.reply_text(f"{word}! how are you today?")
                    bot.send_message(chat_id=update.message.chat_id,text='.', reply_markup=ReplyKeyboardRemove())
                    #Checking for links
            regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
            urls = re.findall(regex,update.message.text)
            for link in urls:
                if link not in allowed_links:
                    if status == "creator" or status == "administrator":
                        pass
                    else:
                        the_reply = update.message.reply_text("Take your links else where!",parse_mode = ParseMode.HTML)
                        reply_message_id = the_reply.message_id
                        time.sleep(5)
                        try:
                            bot.ban_chat_member(chat_id=group_id,user_id=sender_id)
                            bot.delete_message(message_id = reply_message_id,chat_id = group_id)
                            bot.delete_message(message_id = message_id,chat_id = group_id)
                        except:
                            pass
            else:
            pass


def main():
    # Handlers
    new_group_member_handle = MessageHandler(Filters.status_update.new_chat_members, new_group_mamber)
    unknown_handler_command = (MessageHandler(Filters.command, unknown_commands))
    unknown_handler_text = (MessageHandler(Filters.text, unknown_texts))
    
    #Dispatchers
    dispatcher.add_handler(new_group_member_handle)
   
    dispatcher.add_handler(new_group_member_handle)
    dispatcher.add_handler(unknown_handler_command)
    dispatcher.add_handler(unknown_handler_text)
    updater.start_polling()

    web = Flask(__name__)
    @web.route("/")
    def home():
        return "Moderator Bot"
    web.run(threaded=True, host="0.0.0.0", port=_("PORT"))
    updater.idle()

if __name__ == '__main__':
    main()