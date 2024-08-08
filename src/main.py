import os
import AnalScraper  # Ensure this is correctly implemented
import POSTagging


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
    api_key, video_url, num_comments = welcome_message()

     # Call the scraper
    AnalScraper.run_scraper(api_key, video_url, num_comments)

   # top_nouns, top_adjectives = POSTagging.pos_tagging(csv_path)



if __name__ == "__main__":
    main()
