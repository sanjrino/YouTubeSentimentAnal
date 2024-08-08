import os
import torch
import pandas as pd
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

# Define the model directory where the tokenizer and model are saved
model_dir = os.path.dirname(os.path.abspath(__file__))

# Load the tokenizer and model
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained(model_dir, num_labels=3)

# Function to predict sentiment for a batch of sentences
def predict_sentiment(sentences):
    inputs = tokenizer(sentences, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_ids = logits.argmax(dim=1).tolist()
    return predicted_class_ids

# Function to analyze comments
def analyze_comments(comments_file, video_id):
    # Load the comments from the CSV file
    comments_df = pd.read_csv(comments_file)
    comments = comments_df['Comment'].tolist()

    sentiment_counts = {0: 0, 1: 0, 2: 0}

    batch_size = 32  # Process comments in batches to improve efficiency
    for i in range(0, len(comments), batch_size):
        batch = comments[i:i + batch_size]
        # Ensure all comments are strings, had problems
        batch = [str(comment) for comment in batch]
        predicted_class_ids = predict_sentiment(batch)
        for class_id in predicted_class_ids:
            sentiment_counts[class_id] += 1

    total_comments = sum(sentiment_counts.values())
    sentiment_percentages = {label: count / total_comments for label, count in sentiment_counts.items()}

    # Map numeric labels back to string labels
    label_mapping = {0: 'neutral', 1: 'positive', 2: 'negative'}
    sentiment_percentages_mapped = {label_mapping[k]: v for k, v in sentiment_percentages.items()}

    # Display the overall sentiment percentages
    results = []
    for sentiment, percentage in sentiment_percentages_mapped.items():
        formatted_percentage = f"{percentage * 100:.2f}%"
        result = f"{sentiment.capitalize()}: {formatted_percentage} ({percentage:.4f})"
        print(result)
        results.append(result)

    # Save the results to a file
    output_dir = os.path.join(model_dir, '../../data')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'sentiment_fromML_{video_id}.txt')

    # Prepare the results in a formatted string
    formatted_results = "\n".join(results)
    # Return the formatted results
    return formatted_results


if __name__ == "__main__":
    pass #testing thingy
