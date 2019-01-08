import numpy as np
import json

from common import oe_questions, stemmer, opinion_lexicon, clean, survey_df
from nltk.tokenize import word_tokenize


positive_vocab = ['interesting', 'informative', 'satisfied', 'learned', 'good', 'nice', 'great', 'awesome', 'well', 'fantastic', 'enjoy', 'agree']
negative_vocab = ['difficult', 'bad', 'terrible', 'useless', 'hate', 'long', 'boring']

positive_vocab = [stemmer.stem(i) for i in positive_vocab]
negative_vocab = [stemmer.stem(i) for i in negative_vocab]

positive_words = set(opinion_lexicon.positive()).union(positive_vocab)
negative_words = set(opinion_lexicon.negative()).union(negative_vocab)

sentiment_obj = lambda pos, neu, neg: {
  'positive': round(pos, 4),
  'neutral': round(neu, 4),
  'negative': round(neg, 4)
}

def sentiment_of(text):
  if text is np.nan:
    return sentiment_obj(0, 0, 0)

  if not text.endswith('.'):
    text += '.'

  tokenized = word_tokenize(clean(text))
  total = len(tokenized)

  pos = 0
  neg = 0
  neu = 0

  for t in tokenized:
    if t in positive_words:
      pos += 1
    elif t in negative_words:
      neg += 1
    else:
      neu += 1

  return sentiment_obj(pos / total,
                       neu / total,
                       neg / total)


def sentiment_of_answers(answers):
  pos = []
  neu = []
  neg = []

  for a in answers:
    res = sentiment_of(a)
    pos.append(res['positive'])
    neu.append(res['neutral'])
    neg.append(res['negative'])

  return sentiment_obj(np.mean(pos),
                       np.mean(neu),
                       np.mean(neg))


def store_sentiments():
  sentiments = dict()

  for q in oe_questions:
    question = oe_questions[q]
    sentiments[question] = sentiment_of_answers(survey_df[oe_questions[q]])

  with open(f'./data/sentiments.json', 'w+', encoding='utf-8') as f:
    json.dump(sentiments, f, indent=2)

  return sentiments
