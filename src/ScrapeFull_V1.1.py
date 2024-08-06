import requests
from googleapiclient.discovery import build
from googletrans import Translator
from textblob import TextBlob
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from urllib.parse import urlparse, parse_qs

# Read the API key from key.txt
with open('data/key.txt', 'r') as file:
    api_key = file.read().strip()

# Akismet API Key, used to filter spam
akismet_api_key = ""
blog_url = ""


# Function to extract video ID from a YouTube URL
def extract_video_id(url):
    query = urlparse(url).query
    video_id = parse_qs(query).get('v')
    if video_id:
        return video_id[0]
    else:
        raise ValueError("Invalid YouTube URL")


# Build the YouTube client using the API key
youtube = build('youtube', 'v3', developerKey=api_key)


# Function to get comments for a single video, sorted by relevance
# (noticed a lot of spam sorting chronologically and random is impossible to inplement
# unless you first scrape and then later on select random samples, which takes effort.
# This is meant to be only a proof of concept, but in prod it would be considered
def get_sample_comments_for_video(youtube, video_id, max_comments=500):
    comments = []
    try:
        comments += fetch_comments(youtube, video_id, max_comments, order='relevance')
    except Exception as e:
        print(f"An error occurred while fetching comments for video {video_id}: {e}")
    return comments


# Function to fetch comments from YouTube API
def fetch_comments(youtube, video_id, max_comments, order='relevance'):
    comments = []
    page_token = None
    fetched_count = 0

    # Progress bar to show fetching progress
    pbar = tqdm(total=max_comments, desc=f'Fetching comments for video {video_id}', unit=' comment')

    while fetched_count < max_comments:
        try:
            # Requesting comments from YouTube API
            comment_request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                pageToken=page_token,
                textFormat="plainText",
                maxResults=100,  # Max results per request
                order=order
            )
            comment_response = comment_request.execute()

            # Processing each comment
            for item in comment_response['items']:
                top_comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'VideoID': video_id,
                    'Comment': top_comment['textDisplay']
                })
                fetched_count += 1
                pbar.update(1)
                if fetched_count >= max_comments:
                    break

            page_token = comment_response.get('nextPageToken')
            if not page_token:
                break
        except Exception as e:
            print(f"An error occurred while fetching a page of comments: {e}")
            break

    pbar.close()
    return comments


# keep only alphanumeric and all to lower case
def replace_emojis_and_non_alphanumeric(text):
    alphanumeric_pattern = re.compile(r'[^a-zA-Z0-9\s]')
    return alphanumeric_pattern.sub(r'', text)


# Function to check if a comment is spam using Akismet
def detect_spam(comment, api_key, blog_url):
    data = {
        'blog': blog_url,
        'user_ip': '127.0.0.1',  # Dummy IP, replace with actual IP if available
        'user_agent': 'Mozilla/5.0',
        'comment_type': 'comment',
        'comment_author': 'Anonymous',
        'comment_content': comment,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(f'https://rest.akismet.com/1.1/comment-check?key={api_key}', data=data, headers=headers)
    return response.text == 'true'


# Function to autocorrect spelling mistakes in text
def autocorrect_text(text):
    return str(TextBlob(text).correct())


# Function to clean comments, check for spam, and autocorrect text
def process_comment(comment, akismet_api_key, blog_url, translate=False, translator=None):
    try:
        # Clean text
        cleaned_text = replace_emojis_and_non_alphanumeric(comment['Comment'])

        # Detect and skip spam comments
        if detect_spam(cleaned_text, akismet_api_key, blog_url):
            print(f"Spam detected: {cleaned_text}")
            return None

        # Autocorrect text
        corrected_text = autocorrect_text(cleaned_text)

        # Translate text if required
        if translate and translator:
            translated_text = translator.translate(corrected_text, dest='en').text
        else:
            translated_text = corrected_text

        return {
            'VideoID': comment['VideoID'],
            'Comment': translated_text.replace('\n', ' ').replace('\r', ' ')
        }
    except Exception as e:
        print(f"An error occurred while processing a comment: {e}")
        return comment  # If processing fails, use the original comment


# Function to process comments in parallel
def process_comments_parallel(comments, translate=False):
    translator = Translator() if translate else None
    processed_comments = []

    # Using ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        future_to_comment = {
            executor.submit(process_comment, comment, akismet_api_key, blog_url, translate, translator): comment
            for comment in comments}
        for future in tqdm(as_completed(future_to_comment), total=len(comments), desc="Processing comments",
                           unit=" comment"):
            try:
                result = future.result()
                if result:
                    processed_comments.append(result)
            except Exception as e:
                print(f"An error occurred during processing: {e}")

    return processed_comments


# Function to remove duplicate comments
def remove_duplicate_comments(comments):
    seen_comments = set()
    unique_comments = []
    for comment in comments:
        if comment['Comment'] not in seen_comments:
            seen_comments.add(comment['Comment'])
            unique_comments.append(comment)
    return unique_comments


# Function to create POS-ready CSV file
def create_pos_ready_file(comments, video_id):
    pos_ready_comments = []
    for comment in comments:
        pos_ready_comment = comment['Comment'].replace('\n', ' ').replace('\r', ' ').replace(',', ' ')
        pos_ready_comments.append({
            'VideoID': comment['VideoID'],
            'Comment': pos_ready_comment
        })
    pos_ready_df = pd.DataFrame(pos_ready_comments)
    pos_ready_filename = f'POS_ready_{video_id}.csv'
    pos_ready_df.to_csv(pos_ready_filename, index=False)
    print(f'POS-ready comments have been saved to {pos_ready_filename}')


def run_scraper(max_comments, translate, pos_analysis):
    # Prompt user for YouTube link
    video_url = input("Enter the YouTube video URL: ").strip()
    try:
        video_id = extract_video_id(video_url)
    except ValueError as e:
        print(f"Error processing URL: {e}")
        return

    # Fetch comments
    comments = fetch_comments(youtube, video_id, max_comments)

    # Process comments
    processed_comments = [
        process_comment(comment, akismet_api_key, blog_url, translate, Translator() if translate else None) for comment
        in comments]
    processed_comments_df = pd.DataFrame(processed_comments)

    # Remove duplicate rows
    processed_comments_df.drop_duplicates(inplace=True)

    # Save processed comments to CSV file
    processed_output_filename = f'Processed_Comments_{video_id}.csv'
    processed_comments_df.to_csv(processed_output_filename, index=False)
    print(f'Processed comments have been saved to {processed_output_filename}')

    # Create POS-ready file if requested
    if pos_analysis:
        create_pos_ready_file(processed_comments, video_id)


def train_model(max_comments, translate, pos_analysis):
    # Inform the user to update the links.txt file
    input("Please ensure that the links.txt file is updated with the links and titles. Press Enter to continue...")

    # Read the updated links.txt file
    with open('links.txt', 'r') as file:
        lines = file.readlines()

    current_title = ""
    all_comments = []

    for line in lines:
        line = line.strip()

        if line.startswith("@"):
            # @ is the name of the title
            if all_comments and current_title:
                # Remove duplicate comments
                unique_comments = remove_duplicate_comments(all_comments)

                # Process comments
                processed_comments = process_comments_parallel(unique_comments, translate)
                processed_comments_df = pd.DataFrame(processed_comments)

                # Remove duplicate rows
                processed_comments_df.drop_duplicates(inplace=True)

                # Sort by VideoID, to keep video comments separated
                processed_comments_df.sort_values(by=['VideoID'], inplace=True)

                # Save processed comments to CSV file
                processed_output_filename = f'Final_{current_title}.csv'
                processed_comments_df.to_csv(processed_output_filename, index=False)
                print(f'Processed comments for {current_title} have been saved to {processed_output_filename}')

                # Create POS-ready file if requested
                if pos_analysis:
                    create_pos_ready_file(processed_comments, current_title)

            # Start accumulating comments for the new title
            current_title = line[1:]  # Remove @
            all_comments = []

        else:
            try:
                # Extract video ID from the URL
                video_id = extract_video_id(line)
                # Fetch comments for the video
                video_comments = get_sample_comments_for_video(youtube, video_id, max_comments=max_comments)
                all_comments.extend(video_comments)
            except ValueError as e:
                print(f"Error processing URL {line}: {e}")

    # Process the last batch of comments
    if all_comments and current_title:
        unique_comments = remove_duplicate_comments(all_comments)
        processed_comments = process_comments_parallel(unique_comments, translate)
        processed_comments_df = pd.DataFrame(processed_comments)
        processed_comments_df.drop_duplicates(inplace=True)
        processed_comments_df.sort_values(by=['VideoID'], inplace=True)
        processed_output_filename = f'Final_{current_title}.csv'
        processed_comments_df.to_csv(processed_output_filename, index=False)
        print(f'Processed comments for {current_title} have been saved to {processed_output_filename}')

        # Create POS-ready file if requested
        if pos_analysis:
            create_pos_ready_file(processed_comments, current_title)


def main():
    mode = input("Do you want to train the model or just run it? (train/run): ").strip().lower()
    max_comments = input("Enter the number of comments to scrape (default is 500): ")
    if not max_comments.isdigit():
        max_comments = 500
    else:
        max_comments = int(max_comments)

    translate = input("Do you want to translate the comments to English? (yes/no, default is no): ").strip().lower()
    if translate == 'yes':
        translate = True
    else:
        translate = False

    pos_analysis = input("Do you want to prepare comments for POS analysis? (yes/no, default is no): ").strip().lower()
    if pos_analysis == 'yes':
        pos_analysis = True
    else:
        pos_analysis = False

    if mode == 'train':
        train_model(max_comments, translate, pos_analysis)
    elif mode == 'run':
        run_scraper(max_comments, translate, pos_analysis)
    else:
        print("Invalid mode selected. Please choose 'train' or 'run'.")


if __name__ == '__main__':
    main()
