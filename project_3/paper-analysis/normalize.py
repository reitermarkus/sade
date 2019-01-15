#!/usr/bin/env python3

import json
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string

with open('data/papers.json', 'r', encoding = 'utf-8') as f:
  papers = json.load(f)

print(papers)

stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()

def clean(text):
  stop_free = " ".join([w for w in text.lower().split() if w not in stop])
  punc_free = "".join(c for c in stop_free if c not in exclude)
  normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())

  return normalized

normalized_papers = [{'title': clean(p['title']).split(), 'abstract': clean(p['abstract']).split()} for p in papers]

print(normalized_papers)
