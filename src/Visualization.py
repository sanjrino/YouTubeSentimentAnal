import matplotlib.pyplot as plt
from wordcloud import WordCloud

def visualize_data(top_nouns, top_adjectives, positive_percentage, neutral_percentage, negative_percentage, yt_link):
    # create word clouds from top nouns and adjectives
    noun_wc = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(dict(top_nouns))
    adj_wc = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(dict(top_adjectives))

    plt.figure(figsize=(8, 4.5))

    # title and YouTube video link
    plt.suptitle("Comments Analysis Report", fontsize=18, fontweight='bold', y=0.85)
    plt.figtext(0.5, 0.76, f"Video Link: {yt_link}", ha="center", fontsize=8, color="blue", url=yt_link)

    # display the word clouds
    plt.subplot(1, 2, 1)
    plt.imshow(noun_wc)
    plt.title("Top 100 Nouns")
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(adj_wc)
    plt.title("Top 100 Adjectives")
    plt.axis('off')

    # add sentiment percentages
    sentiment_text = (f"Positive: {positive_percentage:.0%} | "
                      f"Neutral: {neutral_percentage:.0%} | "
                      f"Negative: {negative_percentage:.0%}")
    plt.figtext(0.5, 0.2, sentiment_text, ha="center", fontsize=12, bbox={"facecolor": "white", "alpha": 0.5, "pad": 5})

    # save as pdf and show the plot
    plt.savefig("YouTube_Comment_Analysis_Report.pdf", dpi=600)
    plt.show()
