import subprocess
import os
import AnalScraper  # Ensure this is correctly implemented
import POSTagging

#needed for the ML_Anal
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../models/ml_model'))
import ML_Anal

#get req.txt automatically
def install_requirements(requirements_file):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages from {requirements_file}")
        print(e)

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
    requirements_file = "../req.txt"
    install_requirements(requirements_file)

    api_key, video_url, num_comments = welcome_message()

     # Call the scraper
    AnalScraper.run_scraper(api_key, video_url, num_comments)

    #return, do what u want
    csv_path = AnalScraper.run_scraper(api_key, video_url, num_comments)
    top_nouns, top_adjectives = POSTagging.pos_tagging(csv_path)
   # top_nouns, top_adjectives = POSTagging.pos_tagging(csv_path)

    video_id = AnalScraper.extract_video_id(video_url)
    comments_file = f'../data/Processed_Comments_{video_id}.csv'
    ML_Anal.analyze_comments(comments_file, video_id)



if __name__ == "__main__":
    main()
