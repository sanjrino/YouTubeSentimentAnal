# YouTube Sentiment Analyzer
Analyzes YouTube comments to get insights into viewer sentiment, frequently used nouns, and adjectives. Generates a PDF report with viewer sentiment distribution and word clouds.

## Setup
g
### Prerequisites
- Python 3.8+
- Required libraries (auto-installed via `requirements.txt`)

### Installation
1. **Clone the repo:**
   ```bash
   git clone https://github.com/sanjrino/YouTubeSentimentAnal.git
   cd YouTubeSentimentAnalyzer
   ```
2. **Download the model:**
   [Download](https://drive.google.com/drive/folders/12vEgQzEx3cIuglwueAydBsIMoLbjlWvL?usp=sharing) `model.safetensors` and place it in `models/sentiment_analysis` directory.

3. **(Optional) Install dependencies:**
   The necessary dependencies should install automatically when you run main.py, but if you prefer, you can manually install them by running:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. **Run the analysis:**
   ```bash
   python main.py
   ```
   Input your YouTube video link and API key when prompted. The output will be a PDF report named `YouTube_Comments_Analysis_Report_<video_id>.pdf` within the `src` directory.

2. **Review your report:**
   The PDF report will be displayed automatically, allowing you to immediately review the sentiment analysis and insights.

## Disclaimer
This project is intended for educational purposes. The code and model provided are not guaranteed to be free from bugs or errors.

*"If you are looking at the code, I am sorry in advance."*  
— rinosan
