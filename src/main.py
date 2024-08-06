import os
#import AnalScraper
#import POSTagging
#import SentimentAnalysis
#import Visualization


def welcome_message():
    print("Welcome to the YouTube Sentiment Analyzer!\n")

    api_key = get_api_key()

    video_url = input("Enter the YouTube video URL: ")

    num_comments = input("Specify the number of comments to analyze (or type 'all' for all comments): ")

    return api_key, video_url, num_comments


def get_api_key():
    if os.path.exists('../key.txt'):
        with open('../key.txt', 'r') as file:
            api_key = file.read().strip()
        if api_key == "get your own":
            api_key = input("Enter your YouTube API key: ")
            with open('../key.txt', 'w') as file:  # Fixed the path here
                file.write(api_key)
    else:
        api_key = input("Enter your YouTube API key: ")
        with open('../key.txt', 'w') as file:  # Fixed the path here
            file.write(api_key)
    return api_key


def main():
    api_key = get_api_key()
    # The rest of the logic will be handled later
    print(f"API key obtained: {api_key}")


if __name__ == "__main__":
    main()
