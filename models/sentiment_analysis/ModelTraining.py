import pandas as pd
from sklearn.metrics import accuracy_score
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
import torch
from torch.utils.data import Dataset
import time

# Load data
data = pd.read_csv('ReadyToTrain.csv', header=None, names=['video_id', 'comment', 'label'])

# Drop videoID
data = data.drop(columns=['video_id'])

# Filter out unexpected labels
valid_labels = {'neutral', 'positive', 'negative'}
data = data[data['label'].isin(valid_labels)]

# Shuffle the data to randomize row positions
data = data.sample(frac=1, random_state=42).reset_index(drop=True)

# Ensure CSV has the columns 'comment' and 'label'
assert 'comment' in data.columns, "The CSV file does not contain a 'comment' column."
assert 'label' in data.columns, "The CSV file does not contain a 'label' column."

# Separate the data into different classes
positive_data = data[data['label'] == 'positive']
neutral_data = data[data['label'] == 'neutral']
negative_data = data[data['label'] == 'negative']

# Function to split data into 800 training and 200 validation samples for each class
def split_data():
    pos_train, pos_val = positive_data.iloc[:800], positive_data.iloc[800:]
    neu_train, neu_val = neutral_data.iloc[:800], neutral_data.iloc[800:]
    neg_train, neg_val = negative_data.iloc[:800], negative_data.iloc[800:]

    train_data = pd.concat([pos_train, neu_train, neg_train]).sample(frac=1, random_state=42).reset_index(drop=True)
    val_data = pd.concat([pos_val, neu_val, neg_val]).sample(frac=1, random_state=42).reset_index(drop=True)

    train_texts = train_data['comment'].astype(str).tolist()
    train_labels = [label_mapping[label] for label in train_data['label']]
    val_texts = val_data['comment'].astype(str).tolist()
    val_labels = [label_mapping[label] for label in val_data['label']]

    return train_texts, train_labels, val_texts, val_labels

# Map string labels to numeric values
label_mapping = {'neutral': 0, 'positive': 1, 'negative': 2}

# Define function to tokenize data
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

def tokenize_data(texts, labels):
    texts = [str(text) for text in texts]
    encodings = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
    return encodings, torch.tensor(labels)

# Create Dataset class
class SentimentDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item['labels'] = self.labels[idx]
        return item

    def __len__(self):
        return len(self.labels)

# compute metrics
def compute_metrics(p):
    preds = p.predictions.argmax(-1)
    return {'accuracy': accuracy_score(p.label_ids, preds)}

# train and evaluate the model
def train_and_evaluate_model(train_texts, train_labels, val_texts, val_labels, output_dir):
    train_encodings, train_labels = tokenize_data(train_texts, train_labels)
    val_encodings, val_labels = tokenize_data(val_texts, val_labels)

    train_dataset = SentimentDataset(train_encodings, train_labels)
    val_dataset = SentimentDataset(val_encodings, val_labels)

    model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=3)

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=f'{output_dir}/logs',
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="epoch",
        load_best_model_at_end=True,
        fp16=True,  # Enable mixed precision training
        gradient_accumulation_steps=2
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics
    )

    start_time = time.time()
    trainer.train()
    end_time = time.time()

    training_time = end_time - start_time
    print(f"Training time for {output_dir}: {training_time / 60:.2f} minutes")

    # Evaluate the model
    eval_result = trainer.evaluate(eval_dataset=val_dataset)
    print(f"Evaluation results for {output_dir}: {eval_result}")

# Prepare the data
train_texts, train_labels, val_texts, val_labels = split_data()
output_dir = 'results 800 200'

print(f"Number of training samples: {len(train_labels)}")
print(f"Number of validation samples: {len(val_labels)}")
print(f"Training to validation ratio: {(len(train_labels) / len(val_labels)):.2f}")

# Train and evaluate the model
train_and_evaluate_model(train_texts, train_labels, val_texts, val_labels, output_dir)
