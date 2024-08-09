# YouTube Sentiment Analyzer
Analyzes YouTube comments to get insights into viewer sentiment, frequently used nouns, and adjectives. Generates a PDF report with viewer sentiment distribution and word clouds.

- **Sentiment Analysis:** We fine-tuned DistilBERT on a manually labeled dataset of 3,000 comments, sourced from three YouTube categories: music, news, and gaming. You can find the video links we used in `links.txt` in the `data` directory.
  
- **POS Tagging:** For Part-of-Speech (POS) tagging, we trained Conditional Random Fields (CRF) and Maximum Entropy (MaxEnt) models using the Penn Treebank corpus and used it to identify key nouns and adjectives.

## Setup
### Prerequisites
- Python 3.8+
- Required libraries (installed via `req.txt`)
- YouTube API Key

### Installation
1. **Clone the repo:**
   ```bash
   git clone https://github.com/sanjrino/YouTubeSentimentAnal.git
   cd YouTubeSentimentAnalyzer
   ```
2. **Download the model:**
   [Download](https://drive.google.com/drive/folders/12vEgQzEx3cIuglwueAydBsIMoLbjlWvL?usp=sharing) `model.safetensors` and place it in `models/sentiment_analysis` directory.

3. **Install dependencies:**
   Install the necessary dependencies by running:
   ```bash
   pip install -r req.txt
   ```
   It may take a while, so hang in there!

## Usage
1. **Run the analysis:**
   ```bash
   cd src
   python main.py
   ```
   Input your YouTube video link and API key when prompted. The output will be a PDF report named `YouTube_Comments_Analysis_Report_<video_id>.pdf` within the `src` directory.

2. **Review your report:**
   The PDF report will be displayed automatically. Enjoy!

## Disclaimer
This project was intended for educational purposes. The code and model provided are not guaranteed to be free from bugs or errors.

*"If you are looking at the code, I am sorry in advance."*  
— rinosan
