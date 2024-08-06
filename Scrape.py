import requests
from googleapiclient.discovery import build
from deep_translator import GoogleTranslator
from textblob import TextBlob
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

# Read the API key from key.txt
with open('key.txt', 'r') as file:
    api_key = file.read().strip()

# Akismet API Key, used to filter spam
akismet_api_key = ""
blog_url = ""

# Read the URLs and titles from links.txt
with open('links.txt', 'r') as file:
    lines = file.readlines()


# Function to extract video ID from a YouTube URL
def extract_video_id(url):
    from urllib.parse import urlparse, parse_qs
    query = urlparse(url).query
    video_id = parse_qs(query).get('v')
    if video_id:
        return video_id[0]
    else:
        raise ValueError("Invalid YouTube URL")


# Build the YouTube client using the API key
youtube = build('youtube', 'v3', developerKey=api_key)


# Function to get 500 comments for a single video
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
    return alphanumeric_pattern.sub(r'', text).lower()


# Function to check if a comment is spam using Akismet, just copy pasted, will understand later how the API works
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


# Function to autocorrect spelling mistakes in text, not really working but at least it tries
def autocorrect_text(text):
    return str(TextBlob(text).correct())


# Function to translate comment, again not doing great job but better than nothing
# Also deletes spam here
def translate_comment(comment, translator, akismet_api_key, blog_url):
    try:
        # Clean text
        cleaned_text = replace_emojis_and_non_alphanumeric(comment['Comment'])

        # Detect and skip spam comments
        if detect_spam(cleaned_text, akismet_api_key, blog_url):
            print(f"Spam detected: {cleaned_text}")
            return None

        # Autocorrect text
        corrected_text = autocorrect_text(cleaned_text)
        # Translate text
        translated_text = translator.translate(corrected_text)

        return {
            'VideoID': comment['VideoID'],
            'Comment': translated_text.replace('\n', ' ').replace('\r', ' ')
        }
    except Exception as e:
        print(f"An error occurred while translating a comment: {e}")
        return comment  # If translation fails, use the original comment


# Function to translate comments in parallel
def translate_comments_parallel(comments):
    translator = GoogleTranslator(source='auto', target='en')
    translated_comments = []

    # Using ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        future_to_comment = {executor.submit(translate_comment, comment, translator, akismet_api_key, blog_url): comment
                             for comment in comments}
        for future in tqdm(as_completed(future_to_comment), total=len(comments), desc="Translating comments",
                           unit=" comment"):
            try:
                result = future.result()
                if result:
                    translated_comments.append(result)
            except Exception as e:
                print(f"An error occurred during translation: {e}")

    return translated_comments


# Function to remove duplicate comments
def remove_duplicate_comments(comments):
    seen_comments = set()
    unique_comments = []
    for comment in comments:
        if comment['Comment'] not in seen_comments:
            seen_comments.add(comment['Comment'])
            unique_comments.append(comment)
    return unique_comments


# "Main"
current_title = ""
all_comments = []

for line in lines:
    line = line.strip()

    if line.startswith("@"):
        # @ is the name of the title
        if all_comments and current_title:
            # Remove duplicate comments
            unique_comments = remove_duplicate_comments(all_comments)

            # Translate comments
            translated_comments = translate_comments_parallel(unique_comments)
            translated_comments_df = pd.DataFrame(translated_comments)

            # Remove duplicate rows
            translated_comments_df.drop_duplicates(inplace=True)

            # Sort by VideoID, to keep video comments separated
            translated_comments_df.sort_values(by=['VideoID'], inplace=True)

            # Save translated comments to CSV file
            translated_output_filename = f'Final_{current_title}.csv'
            translated_comments_df.to_csv(translated_output_filename, index=False)
            print(f'Translated comments for {current_title} have been saved to {translated_output_filename}')

        # Start acumulating comments for the new title
        current_title = line[1:]  # Remove @
        all_comments = []

    else:
        try:
            # Extract video ID from the URL
            video_id = extract_video_id(line)
            # Fetch comments for the video
            video_comments = get_sample_comments_for_video(youtube, video_id, max_comments=500)
            all_comments.extend(video_comments)
        except ValueError as e:
            print(f"Error processing URL {line}: {e}")

# Process the last batch of comments
if all_comments and current_title:
    unique_comments = remove_duplicate_comments(all_comments)
    translated_comments = translate_comments_parallel(unique_comments)
    translated_comments_df = pd.DataFrame(translated_comments)
    translated_comments_df.drop_duplicates(inplace=True)
    translated_comments_df.sort_values(by=['VideoID'], inplace=True)
    translated_output_filename = f'Final_{current_title}.csv'
    translated_comments_df.to_csv(translated_output_filename, index=False)
    print(f'Translated comments for {current_title} have been saved to {translated_output_filename}')
