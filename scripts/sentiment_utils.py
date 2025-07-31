def count_sentiment_words(text, positive_words, negative_words):
    """
    Count how many positive and negative words appear in the text,
    allowing partial matches for inflections like 'growing', 'declined', etc.
    """
    text = text.lower()
    words = text.split()

    def match(word, keyword_list):
        return any(word.startswith(stem) for stem in keyword_list)

    pos_count = sum(match(word, positive_words) for word in words)
    neg_count = sum(match(word, negative_words) for word in words)

    return pos_count, neg_count
