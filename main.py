from twikit import Client, TooManyRequests
import time
from datetime import datetime
import csv
from configparser import ConfigParser
from random import randint
import os
import sys


MINIMUM_TWEETS = 50
QUERY = '(from:ArweaveEco OR from:aoTheComputer OR from:ar_io_network OR from:ark_defai) arweave dapp permanent ao  @SFBART @Caltrain #ThrowbackThursday lang:en filter:links min_faves:280 since:2018-01-01 until:2020-01-01'


def check_config_file():
    """Check if config.ini exists and has required fields"""
    if not os.path.exists('config.ini'):
        print("❌ config.ini file not found!")
        print("Please create a config.ini file with the following format:")
        print("""
[X]
username = your_username
email = your_email@example.com
password = your_password
        """)
        return False
    
    config = ConfigParser()
    config.read('config.ini')
    
    required_fields = ['username', 'email', 'password']
    missing_fields = []
    
    for field in required_fields:
        if not config.has_option('X', field) or not config.get('X', field).strip():
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing or empty fields in config.ini: {missing_fields}")
        return False
    
    return True


def alternative_scraping_methods():
    """Display alternative methods when twikit fails"""
    print("\n=== Alternative Scraping Methods ===")
    print("1. Official Twitter API v2 (Recommended):")
    print("   - Sign up for Twitter Developer account")
    print("   - Use tweepy library with Bearer token")
    print("   - More reliable and officially supported")
    
    print("\n2. snscrape (No authentication required):")
    print("   - pip install snscrape")
    print("   - Command: snscrape twitter-search 'your query'")
    print("   - Works without login but may be rate-limited")
    
    print("\n3. Selenium automation:")
    print("   - pip install selenium")
    print("   - Automates actual browser interaction")
    print("   - Slower but harder to detect")
    
    print("\n4. Manual export:")
    print("   - Use Twitter's data export feature")
    print("   - Download your data directly from Twitter")


def get_tweets(tweets):
    if tweets is None:
        #* get tweets
        print(f'{datetime.now()} - Getting tweets...')
        tweets = client.search_tweet(QUERY, product='Top')
    else:
        wait_time = randint(5, 10)
        print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds ...')
        time.sleep(wait_time)
        tweets = tweets.next()

    return tweets


#* Check configuration and load credentials
if not check_config_file():
    alternative_scraping_methods()
    sys.exit(1)

config = ConfigParser()
config.read('config.ini')
username = config['X']['username']
email = config['X']['email']
password = config['X']['password']

print(f"Loaded credentials for: {username}")

# #* create a csv file
# with open('tweets.csv', 'w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(['Tweet_count', 'Username', 'Text', 'Created At', 'Retweets', 'Likes'])



#* authenticate to X.com
#! Multiple approaches to handle authentication issues

client = Client(language='en-US')

# Method 1: Try loading existing cookies first (if available)
try:
    print("Attempting to load existing cookies...")
    client.load_cookies('cookies.json')
    print("✅ Successfully loaded cookies!")
    
    # Test if cookies are still valid
    try:
        # Try a simple operation to verify authentication
        test_tweets = client.search_tweet('python', product='Top')
        print("✅ Cookies are still valid!")
    except Exception as e:
        print(f"❌ Cookies expired or invalid: {e}")
        raise Exception("Need fresh login")
        
except (FileNotFoundError, Exception) as e:
    print(f"Cookie loading failed: {e}")
    print("Attempting fresh login...")
    
    # Method 2: Try different login approaches
    login_methods = [
        # Try with different parameter combinations
        {"auth_info_1": username, "password": password},
        {"auth_info_1": email, "password": password},
        {"auth_info_1": username, "auth_info_2": email, "password": password},
    ]
    
    login_successful = False
    for i, method in enumerate(login_methods, 1):
        try:
            print(f"Trying login method {i}...")
            client.login(**method)
            client.save_cookies('cookies.json')
            print(f"✅ Login successful with method {i}!")
            login_successful = True
            break
        except Exception as e:
            print(f"❌ Method {i} failed: {str(e)[:100]}...")
            time.sleep(2)  # Brief delay between attempts
    
    if not login_successful:
        print("\n🚨 All login methods failed!")
        print("\n=== Possible Solutions ===")
        print("1. Check your credentials in config.ini")
        print("2. Enable 2FA and use app passwords")
        print("3. Try again later (Twitter may have temporary restrictions)")
        print("4. Consider using Twitter's official API with Bearer tokens")
        print("5. Use alternative scraping methods")
        
        # Exit gracefully instead of crashing
        alternative_scraping_methods()
        sys.exit(1)

print("✅ Authentication successful! Ready to scrape tweets.")

# Uncomment the following lines to start scraping once authentication works
"""
# Create CSV file
with open('tweets.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Tweet_count', 'Username', 'Text', 'Created At', 'Retweets', 'Likes'])

tweet_count = 0
tweets = None

while tweet_count < MINIMUM_TWEETS:
    try:
        tweets = get_tweets(tweets)
    except TooManyRequests as e:
        rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
        print(f'{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}')
        wait_time = rate_limit_reset - datetime.now()
        time.sleep(wait_time.total_seconds())
        continue

    if not tweets:
        print(f'{datetime.now()} - No more tweets found')
        break

    for tweet in tweets:
        tweet_count += 1
        tweet_data = [tweet_count, tweet.user.name, tweet.text, tweet.created_at, tweet.retweet_count, tweet.favorite_count]
        
        with open('tweets.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(tweet_data)

    print(f'{datetime.now()} - Got {tweet_count} tweets')

print(f'{datetime.now()} - Done! Got {tweet_count} tweets found')
"""