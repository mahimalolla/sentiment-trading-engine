def count_sentiment_words(text, positive_words, negative_words):
    """Count how many positive and negative words appear in the text."""
    pos_count = sum(word in text.lower() for word in positive_words)
    neg_count = sum(word in text.lower() for word in negative_words)
    return pos_count, neg_count
