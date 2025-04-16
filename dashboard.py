import streamlit as st
import pandas as pd
import plotly.express as px
from kafka import KafkaConsumer
import json
from datetime import datetime

# Function to style the dataframe
def style_dataframe(df):
    if df.empty:
        return pd.DataFrame()

    # Make a copy to avoid modifying the original
    display_df = df.copy()

    # Convert timestamp to datetime if it's not already
    if 'timestamp' in display_df.columns:
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp'])
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Reorder columns for better display
    cols = ['timestamp', 'tweet', 'topic', 'sentiment', 'confidence']
    display_cols = [col for col in cols if col in display_df.columns]
    display_df = display_df[display_cols]

    # Rename columns for better display
    display_df = display_df.rename(columns={
        'timestamp': 'Time',
        'tweet': 'Tweet',
        'topic': 'Topic',
        'sentiment': 'Sentiment',
        'confidence': 'Confidence (%)'
    })

    return display_df

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
            st.markdown("""<h2 style='display: flex; align-items: center; gap: 10px;'>
                <span style='font-size: 1.5rem;'>📈</span> Live Sentiment Feed
            </h2>""", unsafe_allow_html=True)

            if not st.session_state.df.empty:
                col1, col2, col3, col4, col5 = st.columns(5)

                total_tweets = len(st.session_state.df)
                col1.metric(
                    label="Total Tweets",
                    value=f"{total_tweets}",
                    delta=None
                )

                positive_count = len(st.session_state.df[st.session_state.df['sentiment'] == 'POSITIVE'])
                positive_pct = (positive_count / total_tweets * 100) if total_tweets > 0 else 0
                col2.metric(
                    label="Positive Sentiment",
                    value=f"{positive_pct:.1f}%",
                    delta=None
                )

                negative_count = len(st.session_state.df[st.session_state.df['sentiment'] == 'NEGATIVE'])
                negative_pct = (negative_count / total_tweets * 100) if total_tweets > 0 else 0
                col3.metric(
                    label="Negative Sentiment",
                    value=f"{negative_pct:.1f}%",
                    delta=None
                )

                neutral_count = len(st.session_state.df[st.session_state.df['sentiment'] == 'NEUTRAL'])
                neutral_pct = (neutral_count / total_tweets * 100) if total_tweets > 0 else 0
                col4.metric(
                    label="Neutral Sentiment",
                    value=f"{neutral_pct:.1f}%",
                    delta=None
                )

                avg_confidence = st.session_state.df['confidence'].mean() if 'confidence' in st.session_state.df.columns else 0
                col5.metric(
                    label="Avg Confidence",
                    value=f"{avg_confidence:.1f}%",
                    delta=None
                )

                st.markdown("<br>", unsafe_allow_html=True)

            display_df = style_dataframe(st.session_state.df.tail(20))

            def highlight_sentiment(val):
                if val == 'POSITIVE':
                    return 'background-color: #8ac926; color: black'
                elif val == 'NEGATIVE':
                    return 'background-color: #ff595e; color: black'
                else:
                    return 'background-color: #ffca3a; color: black'

            styled_df = display_df.style.applymap(highlight_sentiment, subset=['Sentiment'])
            st.dataframe(styled_df, height=400, use_container_width=True)

            # Add sentiment distribution donut chart
            st.markdown("""<h2 style='display: flex; align-items: center; gap: 10px;'>
                <span style='font-size: 1.5rem;'>🍩</span> Sentiment Distribution
            </h2>""", unsafe_allow_html=True)
            fig = px.pie(
                st.session_state.df,
                names="sentiment",
                title="Sentiment Breakdown",
                color="sentiment",
                color_discrete_map={
                    "POSITIVE": "#4CAF50",
                    "NEGATIVE": "#F44336",
                    "NEUTRAL": "#FFC107",
                    "UNKNOWN": "#9E9E9E"
                },
                hole=0.4
            )
            fig.update_traces(textinfo='percent+label', pull=[0.05, 0.05, 0.05, 0.05])
            fig.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=30, b=10, l=10, r=10)
            )
            st.plotly_chart(fig, use_container_width=True)

            # Add sentiment trend over time time series graph
            st.markdown("""<h2 style='display: flex; align-items: center; gap: 10px;'>
                <span style='font-size: 1.5rem;'>📉</span> Sentiment Trend Over Time
            </h2>""", unsafe_allow_html=True)
            fig2 = px.line(
                st.session_state.df,
                x="timestamp",
                y="confidence",
                color="sentiment",
                title="Sentiment Confidence Timeline",
                color_discrete_map={
                    "POSITIVE": "#4CAF50",
                    "NEGATIVE": "#F44336",
                    "NEUTRAL": "#FFC107",
                    "UNKNOWN": "#9E9E9E"
                }
            )
            fig2.update_layout(
                xaxis_title="Time",
                yaxis_title="Confidence (%)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                margin=dict(t=30, b=10, l=10, r=10)
            )
            st.plotly_chart(fig2, use_container_width=True)

# Call the function to start consuming messages
consume_messages()