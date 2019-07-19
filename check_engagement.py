from InstagramAPI import InstagramAPI
import time
from datetime import datetime
import requests
import pprint


API = InstagramAPI("USER", "PASS")
API.login()


likes_list = set()
comments_list = set()

contents = {} #user_id and the usernames that they entered


usernames_from_contents = []

users_that_didnt_engage_list = set()

telegram_usernames_that_didnt_engage = set()

def get_likes_list(media_id, username):

    API.getMediaLikers(media_id)
    f = API.LastJson['users']
    for x in f:
        likes_list.add('@' + x['username'])
    likes_list.add('@' + username)


def check_data(username):

    global users_that_didnt_engage_list

    count = 150 #max number of comments to get
    has_more_comments = True
    max_id = ''
    comments = []

    API.searchUsername(username) #Gets most recent post from user
    info = API.LastJson
    username_id = info['user']['pk']
    user_posts = API.getUserFeed(username_id)
    info = API.LastJson
    media_id = info['items'][0]['id']
    print("mediaid: " + media_id)

    get_likes_list(media_id, username)

    while has_more_comments:
        print("max id: " + max_id)
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
        comments_list.add('@' + comment['user']['username'])
    comments_list.add('@' + username)

    users_that_didnt_engage_list = (users_that_didnt_engage_list | (set(usernames_from_contents) - comments_list | (set(usernames_from_contents) - likes_list)))

    likes_list.clear()
    comments_list.clear()
    
check_this_username = ["justgym8"] #will be replaced with usernames_from_contents

for names in check_this_username:
    check_data(names)
print("These users didn't engage")
print(users_that_didnt_engage_list)

for stuff in users_that_didnt_engage_list:
    for key, value in contents.items():
        if stuff in value:
            telegram_usernames_that_didnt_engage.add(key)

print("These are the telegram users that did not engage: ")
print(telegram_usernames_that_didnt_engage)







    

