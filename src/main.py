import os
import AnalScraper
import POSTagging
import SentimentAnalysis
import Visualization


def welcome_message():
    print("Welcome to the YouTube Sentiment Analyzer!\n")

    api_key = get_api_key()
    video_url = input("Enter the YouTube video URL: ")
    num_comments = input("Specify the number of comments to analyze (or type 'all' for all comments): ")

    return api_key, video_url, num_comments


def get_api_key():
    if os.path.exists('key.txt'):
        with open('key.txt', 'r') as file:
            api_key = file.read().strip()
    else:
        api_key = input("Enter your YouTube API key: ")
        with open('key.txt', 'w') as file:
            file.write(api_key)
    return api_key


def main():
    api_key, video_url, num_comments = welcome_message()

    comments = Scrape.scrape_comments(api_key, video_url, num_comments)

    pos_comments = CleanData.clean_comments_for_pos(comments)
    sentiment_comments = CleanData.clean_comments_for_sentiment(comments)

    top_nouns, top_adjectives = POSTagging.pos_tagging(pos_comments)

    sentiment_results = SentimentAnalysis.sentiment_analysis(sentiment_comments)

    Visualization.visualize_data(top_nouns, top_adjectives, sentiment_results)


if name == "main":
    main()