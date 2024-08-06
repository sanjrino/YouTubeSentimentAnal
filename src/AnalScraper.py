import os
from googleapiclient.discovery import build
import pandas as pd
from tqdm import tqdm
import re
from urllib.parse import urlparse, parse_qs

# Ensure the data directory exists
if not os.path.exists('../data'):
    os.makedirs('../data')

# Function to extract video ID from a YouTube URL
def extract_video_id(url):
    query = urlparse(url).query
    video_id = parse_qs(query).get('v')
    if video_id:
        return video_id[0]
    else:
        raise ValueError("Invalid YouTube URL")

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
                comment_text = clean_comment(top_comment['textDisplay'])
                comments.append({
                    'VideoID': video_id,
                    'Comment': comment_text
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

# Function to clean comments by removing emojis, newlines, and commas
def clean_comment(text):
    text = text.replace('\n', ' ').replace('\r', ' ').replace(',', ' ')
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"  # other symbols
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

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
        pos_ready_comments.append({
            'VideoID': comment['VideoID'],
            'Comment': comment['Comment']
        })
    pos_ready_df = pd.DataFrame(pos_ready_comments)
    pos_ready_filename = f'../data/POS_ready_{video_id}.csv'
    pos_ready_df.to_csv(pos_ready_filename, index=False)
    print(f'POS-ready comments have been saved to {pos_ready_filename}')

def run_scraper(api_key, video_url, max_comments):
    youtube = build('youtube', 'v3', developerKey=api_key)

    try:
        video_id = extract_video_id(video_url)
    except ValueError as e:
        print(f"Error processing URL: {e}")
        return

    if not max_comments.isdigit() and max_comments.lower() != 'all':
        max_comments = 500
    elif max_comments.lower() == 'all':
        max_comments = float('inf')
    else:
        max_comments = int(max_comments)

    # Fetch comments
    comments = fetch_comments(youtube, video_id, max_comments)

    # Process comments
    processed_comments = remove_duplicate_comments(comments)
    processed_comments_df = pd.DataFrame(processed_comments)

    # Save processed comments to CSV file
    processed_output_filename = f'../data/Processed_Comments_{video_id}.csv'
    processed_comments_df.to_csv(processed_output_filename, index=False)
    print(f'Processed comments have been saved to {processed_output_filename}')

    # Create POS-ready file
    create_pos_ready_file(processed_comments, video_id)

if __name__ == '__main__':
    run_scraper()
