#!/usr/bin/env python
import praw
import time
import os
import re
import logging
import logging.handlers
import sys


SearchedSubreddits = ['cigars','cubancigars']
word = ''

# # LOGGING CONFIGURATION # #
LOG_LEVEL = logging.INFO
LOG_FILENAME = "cigarReviewBotInfo.log"
LOG_FILE_BACKUPCOUNT = 5
LOG_FILE_MAXSIZE = 1024 * 256

# ### LOGGING SETUP ### #
log = logging.getLogger("bot")
log.setLevel(LOG_LEVEL)
log_formatter = logging.Formatter('%(levelname)s: %(message)s')
log_formatter_file = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_stderrHandler = logging.StreamHandler()
log_stderrHandler.setFormatter(log_formatter)
log.addHandler(log_stderrHandler)
if LOG_FILENAME is not None:
    log_fileHandler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=LOG_FILE_MAXSIZE, backupCount=LOG_FILE_BACKUPCOUNT)
    log_fileHandler.setFormatter(log_formatter_file)
    log.addHandler(log_fileHandler)

# Authenticate user.User Details should be present in praw.ini file # #
def authenticate():
    reddit = praw.Reddit('cigarReviewbot',user_agent = "Cigar Review Bot v1.2 by /u/devgrv")
    log.info("Bot Authenticated as {}".format(reddit.user.me()))
    return reddit

# # Run bot function # #
def run_bot(reddit):
    log.info("Bot Running...")
    search_cigar_reviews(reddit)


# # Post Submission and comment # #
def repost_submissions(reddit,submission):
    try:
        newSubmission = reddit.subreddit('CigarReview').submit(submission.title,url=submission.url)
        with open("cigar_reviews_posted.txt","a") as f:
                f.write(submission.id + "\n")
        log.info("Post submitted in CigarReview:"+submission.id)
        submission.comment_sort = 'top'
        top_level_comments = list(submission.comments)
        comment_reply = top_level_comments[0].body + "\n\nHere is the link to the original review" +"\n\nhttps://redd.it/" + submission.id
        newSubmission.reply(comment_reply)
        log.info("Comment submitted in CigarReview")
        log.info("###################################################")
    except Exception as e:
        log.info(e)
        error = e.args[0]
        if 'RATELIMIT' in error:
            log.info("Sleeping...Will wake up in 10 mins")
            time.sleep(620)
        elif 'Read timed out' in error:
            log.info("Internet down...Retrying in 60 seconds...")
            time.sleep(60)
        else:
            sys.exit()


# # Search for cigar reviews on subreddit /r/cigars and /r/cubancigars # #
def search_cigar_reviews(reddit):
    cigar_reviews_posted = get_cigar_reviews_posted()
    # log.info(cigar_reviews_posted)
    try:
        for subreddit in SearchedSubreddits:
            for submission in reddit.subreddit(subreddit).search("Review", limit=None):
                for word in submission.title.split():
                    if word.lower() == 'review' and submission.id not in cigar_reviews_posted:
                        repost_submissions(reddit,submission)
    except Exception as e:
        error = e.args[0]
        if 'Read timed out' in error:
            log.info("Internet down...Retrying in 60 seconds...")
            time.sleep(60)



def get_cigar_reviews_posted():
    if not os.path.isfile("cigar_reviews_posted.txt"):
        log.info("Cigar Review file not present...Creating one")
        submissions_reposted = []
    else:
        with open("cigar_reviews_posted.txt","r") as f:
            # log.info("Opening Cigar Review file...")
            submissions_reposted = f.read()
            submissions_reposted = submissions_reposted.split("\n")

    return submissions_reposted

# # START BOT ##
def main():
    try:
        reddit = authenticate()
        while True:
            run_bot(reddit)
    except Exception as e:
        error = e.args[0]
        log.info(e.args[0])
        if '11001' in error:
            log.info("Please check your Internet connection")
            sys.exit()

    



if __name__ ==  '__main__':
    main()


