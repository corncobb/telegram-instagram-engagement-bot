#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram Instagram Engagement Bot by Cameron Cobb

Notes: Possibly take out API when searching for username
       Make sure when adding to groups that "All users are admins" is turned off and you make the bot an admin!!!!!!

Need to do:
    convert usernames_from_contents to Set()
    Get API to check usernames comment and ban non-participating users
    Make this a testing bot and make a new bot
    Detect duplicates when users enter usernames

Done:
    Make this a testing bot and make a new bot
    Fix timezone bullshit
    Remove works
    Turn info from dict into a list
    Fixed spelling errors
    Add emojis
    Add more to help menu
    Get /round command to work properly
    Make sure all print outs say "UTC"
    Make this a testing bot and make a new bot
    Fixed spammy "Drop session not active"
    
"""
from datetime import datetime, time, timedelta
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from InstagramAPI import InstagramAPI
import pytz



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


bot_token = "TOKEN"
groupchatid = "ID" #group chat id

IG_username = 'user'
IG_password = 'pass'


##############################    Important definitions    ##############################

API = InstagramAPI(IG_username, IG_password)

contents = {}
usernames_from_contents = []
users_from_contents = []

utc = pytz.UTC
##########################################################################################

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.


def countdown(HH, MM):
    now = datetime.now(tz=utc)
    target_hour = datetime(year=now.year, month=now.month, day=now.day, hour=HH, minute=MM, second=0, tzinfo=utc)
    return target_hour - datetime.now(tz=utc).replace(microsecond=0)



def interval(message_time):
    if (check_in_interval(time(23,30), time(00,00), message_time) or #11:30 PM - 12:00 AM UTC
            check_in_interval(time(2,30), time(3,00), message_time)or #2:30 AM - 3:00 AM UTC
            check_in_interval(time(5,30), time(6,00), message_time)or #5:30 AM - 6:00 AM UTC
            check_in_interval(time(8,30), time(9,00), message_time)or #8:30 AM - 9:00 AM UTC
            check_in_interval(time(11,30), time(12,00), message_time)or #11:30 AM - 12:00 PM UTC
            check_in_interval(time(14,30), time(15,00), message_time)or #2:30 PM - 3:00 PM UTC
            check_in_interval(time(17,30), time(18,00), message_time)or #5:30 PM - 6:00 PM UTC
            check_in_interval(time(20,30), time(21,00), message_time)): #8:30 PM - 9:00 PM UTC
            return True
    else:
        return False

def check_in_interval(startTime, endTime, nowTime):
    #nowTime = nowTime or datetime.utcnow().time()
    if startTime < endTime:
        return nowTime >= startTime and nowTime <= endTime
    else: #Over midnight
        return nowTime >= startTime or nowTime <= endTime
        

def extract_contents():
    for usernames in contents.keys():
        usernames_from_contents.extend(contents.get(usernames))

    for users in contents:
        users_from_contents.append(users)

def clear_contents(bot, job):
    contents.clear()
    usernames_from_contents.clear()
    users_from_contents.clear()
    #update.message.reply_text("The list has been cleared. This is what is inside:" + str(contents))
    print("The list has been cleared. This is what is inside:" + str(contents))
    print(str(usernames_from_contents))
    print(len(users_from_contents))


def server_start(bot, job):
    bot.send_message(chat_id=groupchatid, text="Server has started or restarted!\n\nCurrent server time is {} UTC.\n\nTo see what was changed and bot info type /version.".format(str(datetime.now(tz=utc).time().replace(microsecond=0))))
    print("Server has started!")
    

def start_drop_message(bot, job):
    bot.send_message(chat_id=groupchatid, text="✅Drop Session Started✅\n\nDrop session will end and round will start at {} UTC.\nDrop usernames (Example: @username1).".format((datetime.utcnow().replace(microsecond=0)) + timedelta(minutes=30)))


def start_round_message(bot, job):

    extract_contents()
    
    keyboard = [[InlineKeyboardButton("📤DM List📤", callback_data='DM List')],
                [InlineKeyboardButton("📱iPhone List📱", callback_data='iPhone List')],
                [InlineKeyboardButton("☎Android List☎", callback_data='Android List')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_message(chat_id=groupchatid, text="🛑Drop Session Ended🛑")
    bot.send_message(chat_id=groupchatid, text="✅Engagement Round Started✅\nTotal usernames: {}\nTotal participants: {}\nYou have 1 hour to like and comment on user's most recent post.\nMake sure you have Private Messaged (PM) me before you choose the list that you want from below:".format(len(usernames_from_contents), len(users_from_contents)), reply_markup=reply_markup)

    

def button(bot, update): 
    query = update.callback_query
    user = update.callback_query.from_user.id

    bot.send_message(chat_id=user, text="Selected option: {}".format(query.data))
    if query.data == 'DM List':
        print_users_dm(bot, update, user)
    elif query.data == 'iPhone List':
        print_users_iphone(bot, update, user)
    elif query.data == 'Android List':
        print_users_android(bot, update, user)


def initiate_drop_session(bot, update):                                                                   
  
    message_time = datetime.now(tz=utc).time()
    groupchat = update.message.chat.id
    print(groupchat)
    if groupchat == groupchatid:
        print(update.message.text + ' ' + str(message_time))
        t = update.message.text    
        if interval(message_time):                          
            if '@' in t:
                if API.searchUsername(update.message.text.replace('@', '')):
                    try:
                        if 1 <= len(contents[update.message.from_user.id]) < 3:
                            contents[update.message.from_user.id].append(update.message.text)
                            update.message.reply_text(update.message.text + " received! " + str(len(contents[update.message.from_user.id])) + "/3 ✅")
                            print(contents)

                        else:
                            update.message.reply_text("Limit reached. You cannot enter anymore usernames🛑")
                            print(contents)
                        
                    except:
                        contents[update.message.from_user.id] = [update.message.text]
                        update.message.reply_text(update.message.text + " received! " + str(len(contents[update.message.from_user.id])) + "/3 ✅")    
                        print(contents)
                        list_len = len(contents)
                        print(list_len)
                else:
                    update.message.reply_text("Username does not exist on Instagram🛑")      
            else:
                update.message.reply_text("Invalid username format🛑\nMake sure you include \"@\" sign when entering username. Example: @username")
                
        #else:
        #    update.message.reply_text("Drop session not active🛑")
        
    else:
        update.message.reply_text("You may only give the bot commands in this chat🛑\nTo drop usernames, you must be in the group chat during round time. Click or type \"/help\" for help.")

def end_round_message(bot, job):
    bot.send_message(chat_id=groupchatid, text="✅Round Completed✅\n\nNext round is at {} UTC.\n\nDrop session will start 30 minutes prior. Use /round to check round and server time.".format((datetime.utcnow().replace(microsecond=0)) + timedelta(hours=1, minutes=30)))

################################################# Print users ############################################################3


def print_users_dm(bot, update, user): #DM list
    for p in usernames_from_contents:
        print(p)

    list_len = len(usernames_from_contents)

    for x in range(0, 90, 10):
        if list_len > x:
            bot.send_message(chat_id=user, text="🔶List {}🔶\n".format(int(x/10 + 1))+'\n'.join(str(p) for p in usernames_from_contents[x:x+10]))
        else:
            break
  

def print_users_iphone(bot, update, user): #link version of list

    list_len = len(usernames_from_contents)
    content = [w.replace('@', '') for w in usernames_from_contents]
    url_content = ["www.instagram.com/" + i for i in content]
    
    print(url_content)

    for x in range(0, 90, 10):
        if list_len > x:
            bot.send_message(chat_id=user, text="🔶List {}🔶\n".format(int(x/10 + 1))+'\n'.join(str(p) for p in url_content[x:x+10]), disable_web_page_preview=True)
        else:
            break

def print_users_android(bot, update, user): #link version of list

    list_len = len(usernames_from_contents)
    content = [w.replace('@', '') for w in usernames_from_contents]
    url_content = ["www.instagram.com/_u/" + i for i in content]
    
    print(url_content)

    for x in range(0, 90, 10):
        if list_len > x:
            bot.send_message(chat_id=user, text="🔶List {}🔶\n".format(int(x/10 + 1))+'\n'.join(str(p) for p in url_content[x:x+10]), disable_web_page_preview=True)
        else:
            break


####################################### COMMANDS ##############################################

def version(bot, update):
    update.message.reply_text("Bot version: 1.1.1 (beta)\n\nLastest update:\n1/6/2018\n- Fixed drop session message.")

    
def help(bot, update):
    groupchat = update.message.chat.id
    if groupchat != groupchatid:
        update.message.reply_text('These are the available commands:\n/contact - contact admin\n/howto - how to participate\n/round - when is next round?\n/times - round times and server time\n/remove - remove entered usernames\n/version - view latest updated on bot')
    else:
        update.message.reply_text('You cannot use this command in this chat. Please PM me to use this command😊') 

def howto(bot, update):
    groupchat = update.message.chat.id
    if groupchat != groupchatid:
        update.message.reply_text("The full instructions for how to participate in this engagement group are on this website: https://www.cameroncobbconsulting.com/instagram-engagement-groups-2019/\n\nIf you have any questions or need clarification please contact admin😊")
    else:
        update.message.reply_text('You cannot use this command in this chat. Please PM me to use this command😊') 


def contact(bot, update):
    groupchat = update.message.chat.id
    if groupchat != groupchatid:
        update.message.reply_text('These are the admins that you can contact:\n@thecameroncobb')
    else:
        update.message.reply_text('You cannot use this command in this chat. Please PM me to use this command😊') 

def round(bot, update):

    if check_in_interval(time(3,00), time(5,30), datetime.now(tz=utc).time()):
        update.message.reply_text('Server time: ' + str(datetime.now(tz=utc).time().replace(microsecond=0)) + ' UTC\n\nTime until next drop session: ' + str(countdown(5,30)))

    elif check_in_interval(time(6,00), time(8,30), datetime.now(tz=utc).time()):
        update.message.reply_text('Server time: ' + str(datetime.now(tz=utc).time().replace(microsecond=0)) + ' UTC\n\nTime until next drop session: ' + str(countdown(8,30)))

    elif check_in_interval(time(9,00), time(11,30), datetime.now(tz=utc).time()):
        update.message.reply_text('Server time: ' + str(datetime.now(tz=utc).time().replace(microsecond=0)) + ' UTC\n\nTime until next drop session: ' + str(countdown(11,30)))
        
    elif check_in_interval(time(12,00), time(14,30), datetime.now(tz=utc).time()):
        update.message.reply_text('Server time: ' + str(datetime.now(tz=utc).time().replace(microsecond=0)) + ' UTC\n\nTime until next drop session: ' + str(countdown(14,30)))
        
    elif check_in_interval(time(15,00), time(17,30), datetime.now(tz=utc).time()):
        update.message.reply_text('Server time: ' + str(datetime.now(tz=utc).time().replace(microsecond=0)) + ' UTC\n\nTime until next drop session: ' + str(countdown(17,30)))
        
    elif check_in_interval(time(18,00), time(20,30), datetime.now(tz=utc).time()):
        update.message.reply_text('Server time: ' + str(datetime.now(tz=utc).time().replace(microsecond=0)) + ' UTC\n\nTime until next drop session: ' + str(countdown(20,30)))
        
    elif check_in_interval(time(21,00), time(23,30), datetime.now(tz=utc).time()):
        update.message.reply_text('Server time: ' + str(datetime.now(tz=utc).time().replace(microsecond=0)) + ' UTC\n\nTime until next drop session: ' + str(countdown(23,30)))
        
    elif check_in_interval(time(0,00), time(2,30), datetime.now(tz=utc).time()):
        update.message.reply_text('Server time: ' + str(datetime.now(tz=utc).time().replace(microsecond=0)) + ' UTC\n\nTime until next drop session: ' + str(countdown(2,30)))
    
    else:
         update.message.reply_text('Server time: ' + str(datetime.now(tz=utc).time().replace(microsecond=0)) + '\nDrop session is currently active. Drop a username! Example: @username')

def times(bot, update):
    update.message.reply_text('Current server time is: ' + str(datetime.now(tz=utc).time().replace(microsecond=0)) + ' UTC\nEngagement rounds are at:\n0:00 UTC\n3:00 UTC\n6:00 UTC\n9:00 UTC\n12:00 UTC\n15:00 UTC\n18:00 UTC\n21:00 UTC\n\nDrop sessions start 30 minutes prior.')
    
def start(bot, update):
    groupchat = update.message.chat.id
    if groupchat != groupchatid:
        update.message.reply_text("Hi! Welcome to the Master Influencer engagement group. This engagement group is temporarily free until a stable release of this bot has been made. Use commands like /help to access more help options. I will also send you the list when you press the button at the end of the round😉\n\nIf you are new to engagement groups or want to know how to participate in this group, please visit https://www.cameroncobbconsulting.com/instagram-engagement-groups-2019/ \n\nPlease contact admin for problems, questions, or complaints.\n\nEnjoy🤗")
    else:
        update.message.reply_text('PM me /start. Don\'t do it in here😊')

def remove(bot, update):
    message_time = datetime.now(tz=utc).time()
    groupchat = update.message.chat.id
    print(groupchat)
    if groupchat == groupchatid:
        print(update.message.text + ' ' + str(message_time))
        if interval(message_time):
            try:
                contents.pop(update.message.from_user.id)
                print(contents)
                update.message.reply_text('All usernames you entered have been removed 0/3 🚮')
            except:
                update.message.reply_text('Usernames have already been removed or you did not enter any usernames🤷‍♂️')
        else:
            update.message.reply_text('You cannot use this command if drop session is not active🛑')
    else:
        update.message.reply_text('You can only use this command in the group chat🛑') 


######################################## ERROR ###########################################
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

####################################### API STUFF ##################################
def get_comment_list(username): 

    count = 100
    has_more_comments = True
    max_id = ''
    comments = []
    username_list = []

    API.searchUsername(username)
    info = API.LastJson
    username_id = info['user']['pk']
    user_posts = API.getUserFeed(username_id)
    info = API.LastJson
    media_id = info['items'][0]['id']


    while has_more_comments:
        _ = API.getMediaComments(media_id, max_id=max_id)
        # comments' page come from older to newer, lets preserve desc order in full list
        for c in reversed(API.LastJson['comments']):
            comments.append(c)
        has_more_comments = API.LastJson.get('has_more_comments', False)
        # evaluate stop conditions
        if count and len(comments) >= count:
            comments = comments[:count]
            # stop loop
            has_more_comments = False
            print("stopped by count")
        # next page
        if has_more_comments:
            max_id = API.LastJson.get('next_max_id', '')
            time.sleep(2)

    for comment in comments:
        username_list.append(comment['user']['username'])
    print(username_list)

###########################################################################

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.

    updater = Updater(bot_token)

    # Set up the Instagram API
    API.login()
    

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    j = updater.job_queue

    j.run_once(server_start, 0)


###################### TIME INTERVALS FOR MESSAGES. ALL IN EASTERN TIME ############################################
    
    for time_ in [datetime(2000, 1, 1, hour=23, minute=30).time(), #23:30
                  datetime(2000, 1, 1, hour=2, minute=30).time(),                 #2:30
                  datetime(2000, 1, 1, hour=5, minute=30).time(),                  #5:30
                  datetime(2000, 1, 1, hour=8, minute=30).time(),                  #8:30
                  datetime(2000, 1, 1, hour=11, minute=30).time(),                  #11:30
                  datetime(2000, 1, 1, hour=14, minute=30).time(),                  #14:30
                  datetime(2000, 1, 1, hour=17, minute=30).time(),                 #17:30
                  datetime(2000, 1, 1, hour=20, minute=30).time()]:                #20:30
                  j.run_daily(start_drop_message, time_)


    for time_ in [datetime(2000, 1, 1, hour=0, minute=00).time(), #0:00 UTC
                  datetime(2000, 1, 1, hour=3, minute=00).time(),                #3:00 UTC
                  datetime(2000, 1, 1, hour=6, minute=00).time(),                 #6:00 UTC
                  datetime(2000, 1, 1, hour=9, minute=00).time(),                 #9:00 UTC
                  datetime(2000, 1, 1, hour=12, minute=00).time(),                 #12:00 UTC
                  datetime(2000, 1, 1, hour=15, minute=00).time(),                #15:00 UTC
                  datetime(2000, 1, 1, hour=18, minute=00).time(),                #18:00 UTC
                  datetime(2000, 1, 1, hour=21, minute=00).time()]:               #21:00 UTC
                  j.run_daily(start_round_message, time_)

    for time_ in [datetime(2000, 1, 1, hour=0+1, minute=00).time(), #1:00 UTC
                  datetime(2000, 1, 1, hour=3+1, minute=00).time(),                #4:00 UTC
                  datetime(2000, 1, 1, hour=6+1, minute=00).time(),                 #7:00 UTC
                  datetime(2000, 1, 1, hour=9+1, minute=00).time(),                 #10:00 UTC
                  datetime(2000, 1, 1, hour=12+1, minute=00).time(),                 #13:00 UTC
                  datetime(2000, 1, 1, hour=15+1, minute=00).time(),                #16:00 UTC
                  datetime(2000, 1, 1, hour=18+1, minute=00).time(),                #19:00 UTC
                  datetime(2000, 1, 1, hour=21+1, minute=00).time()]:               #22:00 UTC
                  j.run_daily(end_round_message, time_)

    for time_ in [datetime(2000, 1, 1, hour=0+1, minute=00+58).time(), #1:58 UTC
                  datetime(2000, 1, 1, hour=3+1, minute=00+58).time(),                #4:58 UTC
                  datetime(2000, 1, 1, hour=6+1, minute=00+58).time(),                 #7:58 UTC
                  datetime(2000, 1, 1, hour=9+1, minute=00+58).time(),                 #10:58 UTC
                  datetime(2000, 1, 1, hour=12+1, minute=00+58).time(),                 #13:58 UTC
                  datetime(2000, 1, 1, hour=15+1, minute=00+58).time(),                #16:58 UTC
                  datetime(2000, 1, 1, hour=18+1, minute=00+58).time(),                #19:58 UTC
                  datetime(2000, 1, 1, hour=21+1, minute=00+58).time()]:               #22:58 UTC
                  j.run_daily(clear_contents, time_)


########################################################################################################

    
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))


    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("howto", howto))
    dp.add_handler(CommandHandler("contact", contact))
    dp.add_handler(CommandHandler("round", round))
    dp.add_handler(CommandHandler("times", times))
    dp.add_handler(CommandHandler("remove", remove))
    dp.add_handler(CommandHandler("version", version))


    dp.add_handler(CallbackQueryHandler(button))

######################## Test commands ############################################
  
    #dp.add_handler(CommandHandler("button", start_round_message)) #Testing purposes
    #dp.add_handler(CommandHandler("drop", start_drop_message))  #Testing purposes
    #dp.add_handler(CommandHandler("end", end_round_message))  #Testing purposes 
    #dp.add_handler(CommandHandler("clear", clear_contents))   #Testing purposes 

################################################################################

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, initiate_drop_session))
    
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    
    updater.idle()


if __name__ == '__main__':
    main()
