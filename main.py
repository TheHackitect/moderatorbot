# Moderator bot for Telegram group chat
# Created by THEHACKITECT 
# Github: https://github.com/thehackitect/moderatorbot
# Website: https://thehackitect.herokuapp.com
#
# import modules
# https://api.telegram.org/bot<API_TOKEN>/getme
# https://api.telegram.org/1233125771/getme


from codecs import replace_errors
import psycopg2
import logging
import time
import json
import re
import itertools
import requests
from flask import Flask,render_template,send_from_directory

# Telegram modukkes
from telegram import *
from telegram import update
from telegram.ext import *
from os import getenv as _
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta


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
        InlineKeyboardButton(text='💬 Telegram', url='https://t.me/thehackitect'),
        InlineKeyboardButton(text='💬 Twitter', url='https://twitter.com/thehackitect'),],
        [InlineKeyboardButton(text='👥 Github', url='https://github.com/thehackitect'),
        InlineKeyboardButton(text='👥 Channel', url='https://t.me/campusbots'),],
        [InlineKeyboardButton(text='🌎 Website', url='https://thehackitect.herokuapp.com'),]
        ]

markup_developer = InlineKeyboardMarkup(developer, one_time_keyboard=True)


def time_stamp_maker(minutes):
    now = datetime.now()
    final_time = now + relativedelta(minutes=minutes)
    return final_time

def start_value(update: Update, context: CallbackContext):
    chat_type = update.effective_chat.type
    if chat_type =='supergroup':
        pass
    else:
        ref_id = update.message.text.replace('/start ','')
        user_data = context.user_data
        user_data['referrer_id'] = ref_id
        x = update.effective_chat
        user_id = x.id
        Name = x.first_name
        target_group_handle = (load_settings()["target_group_username"])
        target_group = (load_settings()["target_group_username"]).replace("@","")
        in_group_status = (bot.get_chat_member(user_id = user_id, chat_id = f"{target_group_handle}")).status
        if in_group_status == "member" or in_group_status == "creator" or in_group_status == "creator":
            try:
                mycursor.execute(f"SELECT ID FROM users_database WHERE ID = '{user_id}' ")
                profile = mycursor.fetchone()[0]
                user_data['telegram_username_request'] = "False"
                keyboard_data3 = (f'{{"type":"Telegram ref link","id":"{user_id}"}}')
                keyboard_data6 = (f'{{"type":"Accumulated Points","id":"{user_id}"}}')
                ref_links = [[InlineKeyboardButton('Telegram Referral',callback_data=f'{keyboard_data3}'),],
                            [InlineKeyboardButton('Accumulated Points',callback_data=f'{keyboard_data6}')]]
                markup_ref_links = InlineKeyboardMarkup(ref_links, resize_keyboard=True, one_time_keyboard=True)
                bot.send_message(chat_id=update.message.chat_id,text=f'Hello {Name}!',parse_mode = ParseMode.HTML,reply_markup = markup_ref_links)
            except:
                mydb.rollback()
                keyboard_data = (f'{{"type":"continue","id":"{user_id}"}}') # this is a dictionary that contains the user ID and the type of informations passed when pressed
                continue_keyboard = [[InlineKeyboardButton('Continue', callback_data=f'{keyboard_data}')]]
                markup_continue_keyboard = InlineKeyboardMarkup(continue_keyboard, one_time_keyboard=True) 
                bot.send_message(chat_id=user_id,text=f'Hello {Name}! Click Continue ...',parse_mode = ParseMode.HTML,reply_markup = markup_continue_keyboard)   
                return ConversationHandler.END

        else:
            keyboard_data = (f'{{"type":"join_group","id":"{user_id}"}}') # this is a dictionary that contains the user ID and the type of informations passed when pressed
            Join_group_keyboard = [[InlineKeyboardButton('Joined✅', callback_data=f'{keyboard_data}'),
                                    InlineKeyboardButton(text='💬 Group', url=f'https://t.me/{target_group}')]]
            markup_Join_group_keyboard = InlineKeyboardMarkup(Join_group_keyboard, one_time_keyboard=True)
            bot.send_message(chat_id = user_id,text=f'Hello {Name}! join group and click joined...',reply_markup = markup_Join_group_keyboard,parse_mode = ParseMode.HTML)


def callback_handler(update: Update, context: CallbackContext):
    target_group = (load_settings()["target_group_username"])
    user_id = update.effective_chat.id
    user_data = context.user_data
    query = update.callback_query
    query.answer()

    callback_info = json.loads(query.data)
    callback_user_id = callback_info["id"]
    callback_type = callback_info["type"]


    if callback_type == "continue":
        name = update.effective_chat.first_name
        username = update.effective_chat.username
        Username = username; points = 0;
        val = (user_id, name,Username, points)
        sql = "INSERT INTO users_database (ID,name,username,points) VALUES (%s, %s, %s, %s)"
        keyboard_data3 = (f'{{"type":"Telegram ref link","id":"{user_id}"}}')
        keyboard_data6 = (f'{{"type":"Accumulated Points","id":"{user_id}"}}')
        ref_links = [[InlineKeyboardButton('Telegram Referral',callback_data=f'{keyboard_data3}'),],
                    [InlineKeyboardButton('Accumulated Points',callback_data=f'{keyboard_data6}')]]
        markup_ref_links = InlineKeyboardMarkup(ref_links, resize_keyboard=True, one_time_keyboard=True)

        
        try:
            mycursor.execute(f"SELECT ID FROM users_database WHERE ID = '{user_id}' ")
            profile = mycursor.fetchone()[0]
            bot.send_message(chat_id=user_id,text=f'Hello {name}!',parse_mode = ParseMode.HTML,reply_markup = markup_ref_links)
        except:
            mydb.rollback()
            mycursor.execute(sql, val)
            mydb.commit()
            try:
                ref_id = user_data['referrer_id']
                mycursor.execute(f"SELECT Points FROM users_database WHERE ID = '{ref_id}' ")
                current_point = mycursor.fetchone()[0]
                new_point = int(current_point) + 1
                mycursor.execute(f"UPDATE users_database SET Points = '{new_point}' WHERE ID = '{ref_id}'")
                mydb.commit()
                bot.send_message(chat_id=user_id,text=f'Hello {name}!',parse_mode = ParseMode.HTML,reply_markup = markup_ref_links)
            except:
                mydb.rollback()
                bot.send_message(chat_id=user_id,text=f'Hello {name}!',parse_mode = ParseMode.HTML,reply_markup = markup_ref_links)


    if callback_type == 'Telegram ref link':
        bot_name = (bot_details()["username"])
        bot_ref_link = f'https://t.me/{bot_name}?start={user_id}'
        bot.send_message(chat_id = user_id,text = f"Your Telegram referral link is:\n\n{bot_ref_link}")  

    elif callback_type == 'Accumulated Points':
        """
        This will check for users accumulated points
        """
        try:
            mycursor.execute(f"SELECT Points FROM users_database WHERE ID = '{user_id}'")
            points = mycursor.fetchone()[0]
            bot.send_message(chat_id = user_id,text = f"You currently have :\n\n{points} Points.")
        except:
            mydb.rollback
            pass
     
    elif callback_type == 'join_group':
        """
        this will certify that a user has joined the telegram group chat
        """       
        try:
            #mycursor.execute(f"SELECT In_group FROM users_database WHERE ID = '{user_id}' ")
            group_id = target_group.replace("@","")
            group_link = f"https://t.me/{group_id}"
            in_group_status = (bot.get_chat_member(user_id = user_id, chat_id = f"{target_group}")).status
            if in_group_status == "member" or in_group_status == "creator" or in_group_status == "administrator":
                user_data = context.user_data
                keyboard_data = (f'{{"type":"continue","id":"{user_id}"}}') # this is a dictionary that contains the user ID and the type of informations passed when pressed
                continue_keyboard = [[InlineKeyboardButton('Continue', callback_data=f'{keyboard_data}')]]
                markup_continue_keyboard = InlineKeyboardMarkup(continue_keyboard, one_time_keyboard=True)
                query.edit_message_text(text = "Confirmed✅")
                #mycursor.execute(f"SELECT * FROM users_database WHERE ID = '{user_id}' ")
                #profile = mycursor.fetchall()[0][0]
                keyboard_data3 = (f'{{"type":"Telegram ref link","id":"{user_id}"}}')
                keyboard_data6 = (f'{{"type":"Accumulated Points","id":"{user_id}"}}')
                ref_links = [[InlineKeyboardButton('Telegram Referral',callback_data=f'{keyboard_data3}'),],
                        [InlineKeyboardButton('Accumulated Points',callback_data=f'{keyboard_data6}')]]
                markup_ref_links = InlineKeyboardMarkup(ref_links, resize_keyboard=True, one_time_keyboard=True)
                bot.send_message(chat_id=callback_user_id,text=f'Welcome!',reply_markup = markup_ref_links) 
                  
                try:
                    referrer = user_data['referrer_id']
                    mycursor.execute(f"SELECT Points FROM users_database WHERE ID = '{referrer}' ")
                    current_point = mycursor.fetchone()[0]
                    new_point = int(current_point) + 1
                    mycursor.execute(f"UPDATE users_database SET Points = '{new_point}' WHERE ID = {referrer}")
                    mydb.commit()
                except:
                    mydb.rollback()
                    bot.send_message(chat_id=user_id,text=f'Welcome {name}! ',parse_mode = ParseMode.HTML,reply_markup = markup_ref_links)   
            else:
                keyboard_data = (f'{{"type":"join_group","id":"{user_id}"}}') # this is a dictionary that contains the user ID and the type of informations passed when pressed
                Join_group_keyboard = [[InlineKeyboardButton('Joined✅', callback_data=f'{keyboard_data}'),
                            InlineKeyboardButton(text='💬 Group', url=group_link)]]
                markup_Join_group_keyboard = InlineKeyboardMarkup(Join_group_keyboard, one_time_keyboard=True)
                try:
                    query.edit_message_text(text = f"<b><i>Kindly join the group, and click the Joined button.</i></b>",reply_markup = markup_Join_group_keyboard,disable_web_page_preview = True,parse_mode=ParseMode.HTML)
                except:
                    query.edit_message_text(text = f"<b><i>You are required to join the group chat and click the joined button!</i></b>",reply_markup = markup_Join_group_keyboard,disable_web_page_preview = True,parse_mode=ParseMode.HTML)
        except:
            mydb.rollback()
            keyboard_data = (f'{{"type":"join_group","id":"{user_id}"}}') # this is a dictionary that contains the user ID and the type of informations passed when pressed
            Join_group_keyboard = [[InlineKeyboardButton('Joined✅', callback_data=f'{keyboard_data}'),
                                    InlineKeyboardButton(text='💬 Group', url=group_link)]]
            markup_Join_group_keyboard = InlineKeyboardMarkup(Join_group_keyboard, one_time_keyboard=True)
            try:
                query.edit_message_text(text = f"You have To join the group chat @ {group_link} and then click the joined button.",reply_markup = markup_Join_group_keyboard,disable_web_page_preview = True)
            except:
                query.edit_message_text(text = f"Join the group chat @ {group_link} and then click the joined button.",reply_markup = markup_Join_group_keyboard,disable_web_page_preview = True)


def get_point(var):
     return var['points']
     
def bot_details():
    url = f"https://api.telegram.org/bot{API_TOKEN}/getme"
    detail = requests.get(url)
    detail = ((json.loads(detail.text))["result"])
    return detail

   
def get_leaderboard(update,chat_type):
    chat_id = update.message.chat_id
    users = list()
    mycursor.execute(f"SELECT Username FROM users_database")
    usernames = mycursor.fetchall()
    mycursor.execute(f"SELECT Name FROM users_database")
    names = mycursor.fetchall()
    mycursor.execute(f"SELECT Points FROM users_database")
    points = mycursor.fetchall()
    

    for (name,username,point) in itertools.zip_longest (names,usernames,points):
        the_dict = {"username":name[0],"points":int(point[0])}
        if username[0] == None or username[0] == "None":
            users.append(the_dict)

        else:
            if "@" in username[0]:
                the_dict = {"username":username[0],"points":int(point[0])}
                users.append(the_dict)
            else:
                the_dict = {"username":f'@{username[0]}',"points":int(point[0])}
                users.append(the_dict)

    assign_badge = list()
    badges = ['🥇','🥈','🥉','🗡','🗡','🗡','🗡','🗡','🗡','🗡']
    users.sort(key=get_point,reverse=True)
    if len(users) < 9:
        for i in range(1):            
            for (user,badge) in itertools.zip_longest (users,badges):
                try:
                    assign_badge.append(f"{badge} {user['username']} number of points {user['points']}")
                except:
                    assign_badge.append(f"{badge} None number of points 0")
                if i == len(users):
                    user == None
                    continue
                elif len(assign_badge) == 9:
                    break
        output = ("\n".join(map(str,assign_badge)))

    else:        
        for (user,badge) in itertools.zip_longest (users,badges):
            assign_badge.append(f"{badge} {user['username']} number of points {user['points']}")
            if len(assign_badge) == 10:
                break
        output = ("\n".join(map(str,assign_badge)))
    if chat_type == "private":
        try:
            message_id = (update.message.reply_text(f"""🏆Leaderboard.\n\nThe following users are on top of the referral contest leaderboard:\n\n{output}""",reply_markup=ReplyKeyboardRemove())).message_id
        except:
            message_id = (update.message.reply_text(f"""🏆 This will show up once there are at least 10 members on the leaderboard.""",reply_markup=ReplyKeyboardRemove())).message_id
    if chat_type == "supergroup":
        try:
            message_id = (update.message.reply_text(f"""🏆Leaderboard.\n\nThe following users are on top of the referral contest leaderboard:\n\n{output}""",reply_markup=ReplyKeyboardRemove())).message_id
        except:
            message_id = (update.message.reply_text(f"""🏆 This will show up once there are at least 10 members on the leaderboard.""",reply_markup=ReplyKeyboardRemove())).message_id       
        time.sleep(4)
        bot.delete_message(chat_id=chat_id,message_id=message_id)
    return output


# Global functions
def check_chat_type(update):
    chat_type = update.effective_chat.type
    if chat_type == "private":
        return  "private"
    elif chat_type == "supergroup":
        return "supergroup"

def force_join_group(user_id):
    target_group = (load_settings()["target_group_username"])
    in_group_status = (bot.get_chat_member(user_id = user_id, chat_id = target_group)).status
    if in_group_status == "member" or in_group_status == "creator" or in_group_status == "administrator":
        return True
    else:
        return False
 

def check_if_user_exist(user_id):
    myresult = mycursor.fetchone()
    if myresult == None:
        return False
    else:
        return True
        
        
def check_if_user_is_admin(user_id,group_id):
    try:
        status = (bot.get_chat_member(user_id = user_id, chat_id = group_id)).status
        if status == "creator" or status == "administrator":
            return True,status
        else:
            return False
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
        return ConversationHandler.END
    in_group = force_join_group(user_id)
    user_exist = check_if_user_exist(user_id)
    admin_status = check_if_user_is_admin(user_id)
    maintenance_status = check_maintenance_status(user_id)

def load_settings():
    with open('settings.json') as data:
        info = json.load(data)
        data.close()
        return info

def new_group_mamber(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        group_id = update.message.chat_id
        group_name =update.effective_chat.title
        text = (load_settings()["welcome_message"])
        message_id = (update.message.reply_text(f"Hi {member.full_name}!\n\nWelcome to <b>{group_name}</b>! <i>{text}</i>",disable_web_page_preview =True,parse_mode = ParseMode.HTML)).message_id 
        time.sleep(5)
        #bot.delete_message(chat_id=group_id,message_id=message_id)

# COMMANDS
def commands(update, context):
    mute_time = (load_settings()["mute_for"])
    ban_time = (load_settings()["ban_for"])
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
        if command == "/developer":
            bot.send_message(chat_id=update.effective_chat.id,text='Contact Developer here',reply_markup=markup_developer)
        elif command == "/leaderboard":
            leaderboard = get_leaderboard(update,chat_type)
        elif command == "/del":
            sql = f"DELETE FROM users_database WHERE ID = {update.message.chat_id}"
            mycursor.execute(sql)
            mydb.commit()
        else:
            bot.send_message(chat_id=update.effective_chat.id,text='❌ Unknown Command! \n reload the Menu by pressing /start')
         
    elif chat_type =='supergroup':
        if status == "creator" or status == "administrator":
            try: 
                if command == "/ban":
                    bot.ban_chat_member(chat_id=group_id,user_id=replied_to_id,revoke_messages=True,until_date=time_stamp_maker(ban_time))
                elif command == "/unban":
                    bot.unban_chat_member(chat_id=group_id,user_id=replied_to_id)
                elif command == "/mute":
                    bot.restrict_chat_member(chat_id=group_id,user_id=replied_to_id,permissions=ChatPermissions(can_send_messages=False),until_date=time_stamp_maker(mute_time))
                elif command == "/unmute":
                    bot.restrict_chat_member(chat_id=group_id,user_id=replied_to_id,permissions=ChatPermissions(can_send_messages=True))
                elif command == "/leaderboard":
                    leaderboard = get_leaderboard(update,chat_type)
                elif command == "/kick":
                    bot.ban_chat_member(chat_id=group_id,user_id=replied_to_id)
                    pass
            except:
                pass
        else:
            pass



def texts(update, context):
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
            data = load_settings()
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
                if status == "creator" or status == "administrator":
                    pass
                elif link in allowed_links:
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

def main():
    # Handlers
    to_start = CommandHandler('start', start_value)
    new_group_member_handle = MessageHandler(Filters.status_update.new_chat_members, new_group_mamber)
    unknown_handler_command = (MessageHandler(Filters.command, commands))
    unknown_handler_text = (MessageHandler(Filters.text, texts))
    
    #Dispatchers
    dispatcher.add_handler(to_start)
    dispatcher.add_handler(CallbackQueryHandler(callback_handler))
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