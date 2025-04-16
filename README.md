<p align="center">
  <a href="#introduction"><strong>Introduction</strong></a> ·
  <a href="#starting-the-app"><strong>Starting the app</strong></a> ·
</p>
<br/>

# Introduction
> Real-Time Sentiment Analysis on Social Media

This project involves collecting real-time social media data using APIs like
Tweepy. The dataset should focus on a specific event, brand, or topic. Students must
preprocess the data by tokenizing text, removing stop words, and cleaning noisy elements
like URLs. Sentiment analysis uses NLP tools, and sentiment trends are visualized over
time. The dashboard should provide live updates of sentiment scores. Deliverables
include the code for real-time data collection, sentiment analysis, a dashboard, and a
report linking sentiment trends to real-world events.
## Dataset
- Real-time data from Twitter, Facebook, or other social media APIs.
- The dataset should cover specific events, topics, or brand mentions over time.
## Tools & Technologies
- [x] Data Collection: Use API calls for real-time data gathering (Tweepy for Twitter).
- [ ] NLP Tools: For sentiment analysis, use natural language processing libraries like
NLTK, TextBlob, or Hugging Face transformers.
- [ ] Real-Time Processing: Apache Kafka or Apache Spark Streaming for real-time
data processing.
## Requirements
- Collect real-time social media data on a specific topic or event.
- Clean and preprocess the text data (tokenization, stop-word removal, etc.).
- Perform sentiment analysis to classify sentiments (positive, negative, neutral).
- Visualize sentiment trends over time.
- Create a dashboard for live updates of sentiment scores.
## Submission
> Midterm Progress Report (3-5 Pages)

- Provide an updated problem description and progress made
so far.
- Discuss related work, methodology, and any preliminary
results.
- Highlight challenges encountered and future steps.

---

> Final Project Report (More than 25 Pages)
- Introduction: Background, motivation, problem definition,
and objectives.
- Related Work: A comprehensive survey of prior studies and
their relevance.
- Methodology: Detailed description of datasets, tools,
techniques, and implementation.

<br/>

# Starting the app
## Start _Zookeeper_
```bash
/Users/thanhhoann/Downloads/kafka_2.13-3.9.0/bin/zookeeper-server-start.sh \
      /Users/thanhhoann/Downloads/kafka_2.13-3.9.0/config/zookeeper.properties
```

## Start _Kafka_ server
```bash
/Users/thanhhoann/Downloads/kafka_2.13-3.9.0/bin/kafka-server-start.sh \
      /Users/thanhhoann/Downloads/kafka_2.13-3.9.0/config/server.properties
```
## Use _Streamlit_
```bash
streamlit run dashboard.py
```

## Run _producer.py_ to produce data
```bash
python3.11 run producer.py
```

## Check _Kafka_ topics
```bash
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```
