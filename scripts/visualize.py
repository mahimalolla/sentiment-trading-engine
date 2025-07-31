import matplotlib.pyplot as plt
from collections import Counter
import os

def plot_sentiment_bar(ticker, pos, neg, output_dir):
    labels = ['Positive', 'Negative']
    values = [pos, neg]
    colors = ['green', 'red']

    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=colors)
    plt.title(f"Sentiment Breakdown for {ticker}")
    plt.ylabel("Keyword Count")
    plt.tight_layout()

    path = os.path.join(output_dir, f"{ticker}_sentiment_bar.png")
    plt.savefig(path)
    plt.close()
    print(f"[SAVED] Bar chart saved to: {path}")

def plot_top_sources_pie(ticker, sources, output_dir):
    source_counts = Counter(sources).most_common(5)
    labels = [s[0] for s in source_counts]
    sizes = [s[1] for s in source_counts]

    plt.figure(figsize=(5, 5))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(f"Top 5 News Sources for {ticker}")
    plt.axis('equal')

    path = os.path.join(output_dir, f"{ticker}_sources_pie.png")
    plt.savefig(path)
    plt.close()
    print(f"[SAVED] Pie chart saved to: {path}")
