# Bayesian Tomatoes:
# Doing some Naive Bayes and Markov Models to do basic sentiment analysis.
#
# Input from train.tsv.zip at
# https:#www.kaggle.com/c/sentiment-analysis-on-movie-reviews
#
# itself gathered from the Rotten Tomatoes movie review aggregation site.
#
# Format is PhraseID[unused]   SentenceID  Sentence[tokenized] Sentiment
#
# We'll only use the first line for each SentenceID, since the others are
# micro-analyzed phrases that would just mess up our counts.
#
# Sentiment is on a 5-point scale:
# 0 - negative
# 1 - somewhat negative
# 2 - neutral
# 3 - somewhat positive
# 4 - positive
#
# For each kind of model, we'll build one model per sentiment category.
# Following Bayesian logic, base rates matter for each category; if critics
# are often negative, that should be a good guess in the absence of other
# information.
#
# Training input is assumed to be in a file called "train.tsv"
#
# Test sentences are received via stdin (thus either interactively or with input redirection).
# Output for each line of input is the following:
#
# Naive Bayes classification (0-4)
# Naive Bayes most likely class's log probability (with default double digits/precision)
# Markov Model classification (0-4)
# Markov Model most likely class's log probability

import math
import sys

import nltk
import numpy as np
from nltk import probability
from nltk.tokenize import word_tokenize
from nltk.util import bigrams

# NLTK is a great toolkit that makes Python a nice choice for natural language processing (NLP)
# ... although to use this tokenizer, you will first need to
# >>> import nltk
# >>> nltk.download('punkt')
# ... to get the dataset it relies on
# Note that bigrams() returns an *iterator* and not a *list* - you will need to call it
# again or store as a list to iterate over the bigrams multiple times

CLASSES = 5
# Assume sentence numbering starts with this number in the file

FIRST_SENTENCE_NUM = 1
# Probability of either a unigram or bigram that hasn't been seen -
# needs to be small enough that it's "practically a rounding error"
OUT_OF_VOCAB_PROB = 0.0000000001


# tokenize():  get words from a line in a consistent way
# uses NLTK, standardizes to lowercase
# returns list of tokens
def tokenize(sentence):
    return [t.lower() for t in word_tokenize(sentence)]


class ModelInfo:
    # ModelInfo fields:
    # word_counts:  5 dicts from string to int, one per sentiment, in a list
    # bigram_counts: same
    # sentiment_counts:  list containing counts of the sentences with different sentiments
    # total_words:  list of counts of words for each sentiment
    # bigram_denoms:  Separate counts of how often a word starts a bigram, again one per sentiment.
    #   (Not quite the same as the word count since last words of sentences aren't counted here)
    # total_bigrams: counts of total bigrams for each sentiment level

    def __init__(self):
        self.word_counts = [{}, {}, {}, {}, {}]
        self.bigram_counts = [{}, {}, {}, {}, {}]
        self.sentiment_counts = [0, 0, 0, 0, 0]
        self.total_words = [0, 0, 0, 0, 0]
        self.bigram_denoms = [{}, {}, {}, {}, {}]
        self.total_bigrams = [0, 0, 0, 0, 0]
        self.total_examples = 0

    # update_word_counts
    # assume space-delimited words/tokens.
    #
    # To "tokenize" the sentence we'll make use of NLTK, a widely-used Python natural language
    # processing (NLP) library.  This will handle otherwise onerous tasks like separating periods
    # from their attached words.  (Unless the periods are decimal points ... it's more complex
    # than you might think.)  The result of tokenization is a list of individual strings that are
    # words or their equivalent.
    #
    # Note that sentiment is an integer, not a string, matching the data format
    def update_word_counts(self, sentence, sentiment):
        # Get the relevant dicts for the sentiment
        s_word_counts = self.word_counts[sentiment]
        s_bigram_counts = self.bigram_counts[sentiment]
        s_bigram_denoms = self.bigram_denoms[sentiment]
        tokens = tokenize(sentence)
        for token in tokens:
            self.total_words[sentiment] += 1
            s_word_counts[token] = s_word_counts.get(token, 0) + 1
        my_bigrams = bigrams(tokens)
        for bigram in my_bigrams:
            s_bigram_counts[bigram] = s_bigram_counts.get(bigram, 0) + 1
            s_bigram_denoms[bigram[0]] = s_bigram_denoms.get(bigram[0], 0) + 1
            self.total_bigrams[sentiment] += 1


# get_models:  returns a model_info object
def get_models():
    next_fresh = FIRST_SENTENCE_NUM
    info = ModelInfo()
    for line in sys.stdin:
        if line.startswith("---"):
            return info
        fields = line.split("\t")
        try:
            sentence_num = int(fields[1])
            if sentence_num != next_fresh:
                continue
            next_fresh += 1
            sentiment = int(fields[3])
            info.sentiment_counts[sentiment] += 1
            info.total_examples += 1
            info.update_word_counts(fields[2], sentiment)
        except ValueError:
            # Some kind of bad input?  Unlikely with our provided data
            continue
    return info


# classify_sentences:  takes a ModelInfo, reads sentences from stdin, prints
# their classification info for the two models
def classify_sentences(info):
    # print("word counts:", info.word_counts)
    # print("bigram counts:", info.bigram_counts)
    # print("sentiment counts:", info.sentiment_counts)
    # print("total words:", info.total_words)
    # print("bigram denoms:", info.bigram_denoms)
    # print("total bigrams:", info.total_bigrams)
    # print("total_examples:", info.total_examples)

    for line in sys.stdin:
        nb_class, nb_logprob = naive_bayes_classify(info, line)
        mm_class, mm_logprob = markov_model_classify(info, line)
        print(nb_class)
        print(nb_logprob)
        print(mm_class)
        print(mm_logprob)

    # naive_bayes_classify:  takes a ModelInfo containing all counts necessary for classsification


# and a String to be classified.  Returns a number indicating sentiment and a log probability
# of that sentiment (two comma-separated return values).
def naive_bayes_classify(info, sentence):
    prob_sentiment_sentence = []
    words = tokenize(sentence)
    for s in range(CLASSES):  # get probability of each sentiment for sentence
        prob_sentiment = info.sentiment_counts[s] / \
            sum(info.sentiment_counts)
        prob_sentence = 0
        for word in words:  # iterate through each word to get probability
            try:
                prob_word = info.word_counts[s][word] / \
                    sum(info.word_counts[s].values())
            except KeyError:
                prob_word = OUT_OF_VOCAB_PROB  # word not present in sentiment
            # use log to avoid multiplying
            prob_sentence += math.log(prob_word)
        prob_sentiment_sentence.append(math.log(prob_sentiment)+prob_sentence)

    # best class, log probability
    return np.argmax(prob_sentiment_sentence), max(prob_sentiment_sentence)


# markov_model_classify:  like naive Bayes, but now use a bigram model.  First word
# still uses unigram count & probability.
def markov_model_classify(info, sentence):
    prob_sentiment_sentence = []
    words = tokenize(sentence)
    for s in range(CLASSES):  # get probability of each sentiment for sentence
        prob_sentiment = info.sentiment_counts[s] / \
            sum(info.sentiment_counts)
        prob_sentence = 0
        # iterate through each word to get probability
        for word_num in range(len(words)):
            if word_num == 0:  # no bigram for first word
                try:
                    prob_word = info.word_counts[s][words[0]] / \
                        sum(info.word_counts[s].values())
                except KeyError:
                    prob_word = OUT_OF_VOCAB_PROB  # word not present in sentiment
                # use log to avoid multiplying
                prob_sentence += math.log(prob_word)
            else:
                bigram = (words[word_num-1], words[word_num])
                try:
                    prob_word = info.bigram_counts[s][bigram] / \
                        (info.bigram_denoms[s][words[word_num-1]])
                except KeyError:
                    prob_word = OUT_OF_VOCAB_PROB  # bigram not present in sentiment
                # use log to avoid multiplying
                prob_sentence += math.log(prob_word)
        prob_sentiment_sentence.append(math.log(prob_sentiment)+prob_sentence)

    # best class, log probability
    return np.argmax(prob_sentiment_sentence), max(prob_sentiment_sentence)


if __name__ == "__main__":
    info = get_models()
    classify_sentences(info)
