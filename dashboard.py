import streamlit as st
import pandas as pd
import plotly.express as px
from kafka import KafkaConsumer
import json

# Initialize Kafka Consumer for processed data
consumer = KafkaConsumer(
    'sentiment_analysis',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Streamlit UI
st.set_page_config(layout="wide")
st.title("📊 Real-Time Sentiment Analysis Dashboard")

# Initialize session state for persistent storage
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["timestamp", "sentiment", "confidence"])

placeholder = st.empty()  # Placeholder for dynamic UI updates

def consume_messages():
    for message in consumer:
        new_data = message.value

        # Append new data to session state DataFrame
        new_row = pd.DataFrame([new_data])
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)

        with placeholder.container():
            st.subheader("Live Sentiment Feed")
            st.write(st.session_state.df.tail(10))

            # Sentiment Distribution
            st.subheader("Sentiment Distribution")
            fig = px.pie(st.session_state.df, names="sentiment", title="Sentiment Breakdown")
            st.plotly_chart(fig)

            # Time-based sentiment trends
            st.subheader("Sentiment Trend Over Time")
            fig2 = px.line(st.session_state.df, x="timestamp", y="confidence", title="Sentiment Confidence Timeline")
            st.plotly_chart(fig2)

# Call the function to start consuming messages
consume_messages()
