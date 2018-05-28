# -*- coding: utf-8 -*-
# 17/01/2018

import json
import datetime
import csv
import time
import datetime
import pprint
import sys
import os

# set since 3000 recursions, for post with >= 25000 comments
sys.setrecursionlimit(3000)

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

app_id = ""
app_secret = ""  # DO NOT SHARE WITH ANYONE!
# !!GOOD BOTH FOR PAGE AND FOR GROUPS!!
page_id = "" # page: https://www.facebook.com/!!THIS PART!!/
num_post = 0
num_comments = 0
num_comm_per_page = 25

def add_num_post(value):
    global num_post
    num_post = num_post + value

def add_num_comments(value):
    global num_comments
    num_comments = num_comments + value

def request_until_succeed(url):
    req = Request(url)
    success = False
    while success is False:
        try:
            response = urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)
            time.sleep(5)

            print("Error for URL {}: {}".format(url, datetime.datetime.now()))
            print("Retrying.")

    return response.read()


def writeFile(path, name, text):
    write_file = open(path + name,"w+")
    write_file.write(text)
    write_file.close()

# The function for taking comments is recursive. Comments are taken 25 at a time.
# There is a maximum number of recursion for the python interpreter (= 1000).
# If the post has a number of comments > 25000 (25000/25 = 1000), our interpreter crash.
# This function is useful for dynamically increase the maximum number of recursions possible by the Python interpreter
def set_recursion_limit(total_comments):
    for key, value in total_comments.iteritems() :
        if key=="total_count":
            sys.setrecursionlimit( value/num_comm_per_page )

####################################################################
#                       SCRAPING POSTs                             #
####################################################################

# first request will be of the type:
# https://graph.facebook.com/v2.11/page_id/posts?access_token=....
# then, will be gather all the values next in the json file in order to do at the next request
def scrape_first_posts_in_page(page_id, access_token):
    base = "https://graph.facebook.com/v2.11/"
    parameters = "&access_token={}".format(access_token)
    fields = "?fields=posts"
    num_page = 1

    url = base + page_id + fields + parameters
    #print(url)
    print("\n scraping posts in page: " + str(num_page))
    json_downloaded = request_until_succeed(url)
    data = json.loads(json_downloaded)['posts']['data'] # Json(casted in list) data from our request
    next_post = json.loads(json_downloaded)['posts']['paging'] # this are used for take 'next' element in the dictionary
    for key, value in next_post.iteritems() :
        if key=="next":
            next_value = value

    writeFile("./posts/", str(num_page) + ".next_value.txt", next_value)
    print("\n writing "+ str(num_page) +" next_value")

    loops_for_scraping_comments(num_page, data)

    scrape_all_posts_in_page(next_value, num_page + 1)

def scrape_all_posts_in_page(url, num_page):
    json_downloaded = request_until_succeed(url)
    data = json.loads(json_downloaded)['data'] # Json(casted in dictionary) data from our request
    next_post = json.loads(json_downloaded)['paging'] # this are used for take 'next' element in the dictionary

    #pp = pprint.PrettyPrinter(indent=2)
    #pp.pprint(next_post)
    for key, value in next_post.iteritems() :
        if key=="next":
            next_value = value
            writeFile("./posts/", str(num_page) + ".next_value", value)
            print("\n writing "+ str(num_page) +" next_value")

    print("\n scraping posts in page: " + str(num_page))

    loops_for_scraping_comments(num_page, data)

    scrape_all_posts_in_page(next_value, num_page + 1)

####################################################################
#                       SCRAPE POST'S COMMENTS                     #
####################################################################

# function for scrape single post's comments
def loops_for_scraping_comments(num_page, data):
    # retrieve data, message and id (useful for querying the comments)
    extension=".json"
    i = 0
    #print(len(data))
    #count num_post
    add_num_post(len(data))

    while (i < len(data)):
        print("\n   scraping post " + str(i + 1)  + " in page: " + str(num_page))

        created_time = data[i]['created_time']

        # use get method over the dictionary because the comment couldn't exist and Facebook doesn't generate the corresponding item in the Json file
        if data[i].get('message') is None:
            message = ""
        else:
            message = data[i].get('message').encode("utf-8")

        id_post = data[i]['id']
        scrape_starttime = datetime.datetime.now()
        comments = scrape_first_comments_from_post_id(id_post, access_token)
        print("   Done! Comment Processed in {}".format(datetime.datetime.now() - scrape_starttime))

        name_file =  str(created_time).replace(':','.') + "page_" + str(num_page) + "_posts" + str(i + 1)
        writeFile("./posts/", name_file + extension, str(created_time) + "\n\n" + str(message) + "\n\n" + str(id_post) + "\n\n" + str(comments) + "\n\n")

        i = i + 1

def scrape_first_comments_from_post_id(post_id, access_token):
    # with filter=stream should also gather the aswers to comments, but it seems doesn't work
    # https://graph.facebook.com/v2.11/post_id/comments?filter=stream&summary=true&access_token=2081983152047773|cUqdwRV6VnEZBTwAwmv5wdBQEBw
    base = "https://graph.facebook.com/v2.11/"
    parameters = "&access_token={}".format(access_token)
    fields = "/comments?filter=stream&summary=true"

    scr_data = []
    url= base + post_id + fields + parameters
    json_downloaded = request_until_succeed(url)

    data = json.loads(json_downloaded)['data']

    if json.loads(json_downloaded).get('paging') is None:
        next_post = {}
    else:
        next_post = json.loads(json_downloaded).get('paging')

    total_comments = json.loads(json_downloaded)['summary']

    #set_recursion_limit(total_comments)

    comment_count = 0
    for count in data:
        comment_count += 1

    #count comments
    add_num_comments(comment_count)

    #search next post url
    for key, value in next_post.iteritems() :
        if key=="next":
            scr_data = scrape_all_comments_from_post_id(value)

    return data + scr_data

def scrape_all_comments_from_post_id(url):
    scr_data = []
    json_downloaded = request_until_succeed(url)

    data = json.loads(json_downloaded)['data'] # Json(casted in dictionary) data from our request
    next_post = json.loads(json_downloaded)['paging'] # this are used for take 'next' element in the dictionary

    comment_count = 0
    for count in data:
        comment_count += 1

    #count comments
    add_num_comments(comment_count)

    for key, value in next_post.iteritems() :
        if key=="next":
            scr_data = scrape_all_comments_from_post_id(value)

    return data + scr_data



if __name__ == '__main__':

    filename_n_v = []

    for filename in os.listdir('./posts/'):
        if filename.endswith(".next_value"):
            filename_n_v.append(filename)


    num_page = 1


    print("Request token")
    #new access_token
    access_token_request = request_until_succeed("https://graph.facebook.com/v2.11/oauth/access_token?client_id=" + app_id + "&client_secret=" + app_secret + "&grant_type=client_credentials")
    access_token = json.loads(access_token_request)["access_token"] #!type unicode!
    print("fresh access token: " + access_token + "\n")

    url="https://graph.facebook.com/v2.11/"+ page_id +"/posts?access_token=" + access_token + "&limit=25"

    scrape_starttime = datetime.datetime.now()
    # start scraping's post phase
    print("Scraping's posts phase start...\n")

    # start from begin
    # scrape_first_posts_in_page(page_id, access_token)

    # start from a block's posts
    # files with next_value extension are:
    # 1.next_value = i post che vanno da 26 a 50
    # 2.next_value = i post che vanno da 51 a 75 etc...
    scrape_all_posts_in_page(url, num_page)

    print("\nScraping's posts phase stop...")

    print("\nDone!\n{} Comments Processed in {}".format(
            num_processed, datetime.datetime.now() - scrape_starttime))
