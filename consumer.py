from kafka import KafkaConsumer, KafkaProducer
import json
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize Kafka Consumer & Producer
consumer = KafkaConsumer(
    "sentiment_topic",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Initialize Sentiment Analyzers
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    # Using VADER for sentiment analysis
    scores = analyzer.polarity_scores(text)
    compound_score = scores["compound"]

    if compound_score >= 0.05:
        return "positive"
    elif compound_score <= -0.05:
        return "negative"
    else:
        return "neutral"

# Process tweets and classify sentiment
for message in consumer:
    tweet = message.value
    sentiment = analyze_sentiment(tweet["text"])

    # Add sentiment classification to data
    tweet["sentiment"] = sentiment
    print(f"Processed: {tweet}")

    # Send the processed tweet to a new Kafka topic
    producer.send("sentiment_analysis", tweet)
