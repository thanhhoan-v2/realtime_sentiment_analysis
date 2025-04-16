from flair.models import TextClassifier
from flair.data import Sentence
import re
import time
from kafka import KafkaProducer
import json
from datetime import datetime
import random

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Define multiple search topics
SEARCH_TOPICS = ["Tesla", "Apple", "Climate Change", "Cryptocurrency", "AI"]

# Dummy tweets with predetermined sentiments
POSITIVE_TWEETS = [
    "I absolutely love my new {topic} product! Best purchase I've made this year.",
    "The latest {topic} innovation is incredible. This will change everything!",
    "{topic} just announced amazing new features that will revolutionize the industry.",
    "Just had a great experience with {topic} customer service. They really care about their customers!",
    "The {topic} community is so supportive and positive. Proud to be part of it!",
    "The future of {topic} looks incredibly bright. Excited to see what's next!",
    "My investment in {topic} has been performing exceptionally well. Great returns!",
    "{topic} is leading the way in sustainability efforts. Setting a great example!",
    "The new {topic} update has significantly improved performance. Very impressed!",
    "Just attended a {topic} conference and was blown away by the innovations."
]

NEGATIVE_TWEETS = [
    "Really disappointed with my recent {topic} purchase. Not worth the money at all.",
    "The latest {topic} announcement was a complete letdown. They're falling behind.",
    "{topic} customer service is terrible. Been waiting for a response for days.",
    "The quality of {topic} products has seriously declined over the years.",
    "Frustrated with all the issues I'm having with {topic}. Might switch to a competitor.",
    "{topic} prices are getting ridiculous. They're just exploiting their customers now.",
    "The {topic} community has become so toxic lately. Really sad to see.",
    "My investment in {topic} is tanking. Should have listened to the warnings.",
    "The environmental impact of {topic} is concerning. They need to do better.",
    "The new {topic} policy changes are a disaster. They've lost touch with their users."
]

NEUTRAL_TWEETS = [
    "Just read an article about {topic}. Interesting developments in the industry.",
    "{topic} announced their quarterly results today. Numbers were as expected.",
    "Wondering what the future holds for {topic} in the next few years.",
    "Comparing different {topic} options before making a decision.",
    "The history of {topic} development is quite fascinating to study.",
    "Looking for recommendations on {topic} resources. Any suggestions?",
    "{topic} market share remained stable this quarter according to reports.",
    "Attended a workshop about {topic} today. Learned some new information.",
    "The debate around {topic} regulation continues with valid points on both sides.",
    "Researching {topic} for a project. There's a lot of information to process."
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

# Load sentiment classifier
classifier = TextClassifier.load('en-sentiment')

# Function to analyze sentiment of a tweet
def analyze_tweet_sentiment(text):
    # Create a Sentence object from the input text
    tweet_sentence = Sentence(text)
    # Use the classifier to predict sentiment
    classifier.predict(tweet_sentence)
    # Ensure there is a label before extracting it
    if tweet_sentence.labels:
        sentiment_label = tweet_sentence.labels[0].value  # 'POSITIVE' or 'NEGATIVE'
        confidence = tweet_sentence.labels[0].score * 100  # Convert confidence to percentage
        return sentiment_label, confidence
    else:
        return "NEUTRAL", 50.0  # Handle cases where no sentiment is detected

def generate_dummy_tweet():
    # Select a random topic
    topic = random.choice(SEARCH_TOPICS)

    # Determine sentiment type with equal probability
    sentiment_type = random.choice(["positive", "negative", "neutral"])

    # Select a random tweet template based on sentiment
    if sentiment_type == "positive":
        tweet_template = random.choice(POSITIVE_TWEETS)
        expected_sentiment = "POSITIVE"
        confidence_base = 70.0
    elif sentiment_type == "negative":
        tweet_template = random.choice(NEGATIVE_TWEETS)
        expected_sentiment = "NEGATIVE"
        confidence_base = 70.0
    else:
        tweet_template = random.choice(NEUTRAL_TWEETS)
        expected_sentiment = "NEUTRAL"
        confidence_base = 50.0

    # Fill in the topic
    tweet = tweet_template.format(topic=topic)

    # Add some randomness to confidence
    confidence = confidence_base + random.uniform(-10.0, 10.0)
    confidence = min(max(confidence, 40.0), 95.0)  # Keep within reasonable bounds

    return tweet, expected_sentiment, confidence, topic

# Main loop to generate and send tweets
def main():
    print("Starting dummy tweet producer...")
    try:
        while True:
            # Generate a dummy tweet
            tweet, expected_sentiment, confidence, topic = generate_dummy_tweet()

            # Clean the tweet
            cleaned_tweet = clean_text(tweet)

            # For realism, sometimes use the classifier instead of predetermined sentiment
            if random.random() < 0.3:  # 30% chance to use the classifier
                sentiment, confidence = analyze_tweet_sentiment(cleaned_tweet)
            else:
                sentiment = expected_sentiment

            # Prepare data for Kafka
            data = {
                'tweet': tweet,
                'topic': topic,
                'sentiment': sentiment,
                'confidence': confidence,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Send to Kafka
            producer.send('sentiment_analysis', value=data)

            # Print for debugging
            print(f"Topic: {topic}")
            print(f"Tweet: {tweet}")
            print(f"Sentiment: {sentiment} ({confidence:.2f}%)\n")

            # Sleep to avoid flooding
            time.sleep(random.uniform(0.5, 2.0))

    except KeyboardInterrupt:
        print("Stopping producer...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    main()
