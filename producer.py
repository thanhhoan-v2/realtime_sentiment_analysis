import tweepy
import re
import time
from kafka import KafkaProducer
import json
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Set up X API credentials
access_token = "1900207915161808896-J8fRt3i0mufOQfLzwjhZOP1tJmhuT7"
access_token_secret = "JDIhjsZ0aLDU6dU09x7gv5wmQvqdbTgiypzIAunBnPq4c"
client_id = "NlRvM2xvdHZPQXZiUHZkWS1yb0Q6MTpjaQ"
client_secret = "TRK6WWcTkUCt0Vrfqbu_fS5cf-eUXptwUDg8_VdqgBTDXzBlC6"
consumer_key = "ArsTGZ8y1lkSdGkG0GaOzNNZD"
consumer_secret = "hqUpa8yJKyOqJnytmKpFOq8dPXE2J84bYKtJCdsw4QP6cZpCNz"
bearer_token = "AAAAAAAAAAAAAAAAAAAAABmpzwEAAAAATz53%2FQkHJ3is9wSvM9fnUgdM3%2Bs%3DzEi8Pj85uDve0o3uKuVSnWnfdDLAULc9OX3VyDMMVVhCTsmPat"

# Initialize Tweepy client
tweepyClient = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret)
tweepyClient.get_me()

# Set up search query
searchQuery = "Tesla"

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Dummy tweets to use when the Twitter API is unavailable
DUMMY_TWEETS = [
     "RT @EndWokeness: I am baffled by the lack of action taken by the DOJ over left-wing domestic terror.",
     "🚀🌿 The Future is Here – and We’re Creating It! Just like Tesla, our project Junona is built on technology...",
     "#Tesla's shares have been hit even harder, crashing 30% over the month and seeing their biggest one-day dive in 4 ½ years.",
     "RT @LoomerUnleashed: 🚨The organizer of the Tesla Takedown protest scheduled for Friday, March 14, 2025 at the Tesla Showroom...",
     "Soros gave 7.6 million dollars to Indivisible, the group who has waged a global Intifada against Tesla.",
     "@rodjo1 Ne bih se slozio. Elon ima samo 13% kompanije.",
     "Vandalism at a Tesla Dealership is not domestic terrorism. This is.👇👇👇"
]

# Function to clean text
def clean_text(input_text):
    # Change all characters to lowercase
    processed_text = input_text.lower()
    # Eliminate username mentions
    processed_text = re.sub("@[\w]*", "", processed_text)
    # Strip out website URLs
    processed_text = re.sub("http\S+", "", processed_text)
    # Remove numbers and special symbols
    processed_text = re.sub("[^a-zA-Z#]", " ", processed_text)
    # Delete 'rt' markers
    processed_text = re.sub("rt", "", processed_text)
    # Normalize whitespace
    processed_text = re.sub("\s+", " ", processed_text).strip()

    return processed_text

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Function to analyze sentiment of a tweet
def analyze_tweet_sentiment(text):
    # Use VADER to analyze sentiment
    scores = analyzer.polarity_scores(text)
    compound_score = scores["compound"]

    # Determine sentiment based on compound score
    if compound_score >= 0.05:
        sentiment_label = "POSITIVE"
    elif compound_score <= -0.05:
        sentiment_label = "NEGATIVE"
    else:
        sentiment_label = "NEUTRAL"

    # Calculate confidence (normalize compound score to a percentage)
    # Convert the absolute compound score to a confidence percentage between 50-95%
    confidence = 50.0 + (abs(compound_score) * 45.0)

    return sentiment_label, confidence

def get_tweets():
    tweets = None
    try:
        tweets = tweepyClient.search_recent_tweets(query=searchQuery).data
        return [tweet.text for tweet in tweets] if tweets else DUMMY_TWEETS
    except tweepy.errors.TooManyRequests:
        print("Rate limit exceeded. Returning dummy tweets.")
    except tweepy.errors.TweepyException as e:
        print(f"Twitter API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    if not tweets:
        return DUMMY_TWEETS
    return tweets


for tweet in get_tweets():
    cleaned_tweet = clean_text(tweet)
    sentiment, confidence = analyze_tweet_sentiment(cleaned_tweet)
    data = {
        'tweet': tweet,
        # 'cleaned_tweet': cleaned_tweet,
        'sentiment': sentiment,
        'confidence': confidence,
        'timestamp': datetime.utcnow().isoformat()  # Add timestamp
    }
    producer.send('sentiment_analysis', value=data)
    print(f"Tweet: {tweet}\nSentiment: {sentiment} ({confidence:.2f}%)\n")
    time.sleep(1)  # To avoid flooding the Kafka server
