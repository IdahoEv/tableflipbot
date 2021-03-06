import time
import requests
import logging
from bs4 import BeautifulSoup

from flipper import get_flipped_string

SLEEP_INTERVAL = 60 * 60 * 12 # Twice a day


def get_word_of_day():

    try:
        
        oxford_homepage = requests.get("http://www.oed.com/")
        soup = BeautifulSoup(oxford_homepage.text)

        wod = soup.select(".wordOfTheDay .hw")

        if len(wod):
            word_text = wod.pop().text.lower().strip()
            return word_text
        else:
            return None

    except Exception:
        return None


def flip_word_of_day(api, redis_client, redis_used_key):

    while True:

        word_of_day = get_word_of_day()

        # If we were able to parse
        if word_of_day:

            flipped_wod = get_flipped_string(word_of_day.decode('utf-8'))
            logging.info("Flipped text (%s) to: %s" % (word_of_day, flipped_wod.decode('utf-8')))

            # If we haven't already flipped it, tweet and add to set
            if not redis_client.sismember(redis_used_key, word_of_day):
                tweet = flipped_wod
                api.update_status(tweet)
                redis_client.sadd(redis_used_key, word_of_day)
            else:
                logging.info("Already tweeted this, skipping")


        else:
            logging.info("Unable to parse the word of the day.")

        time.sleep(SLEEP_INTERVAL)



if __name__ == "__main__":

    word_of_day = get_word_of_day()
    print word_of_day
    print get_flipped_string(word_of_day.decode('utf-8'))
    

