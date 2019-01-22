#!/usr/bin/env python3

import re

from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize

import string

stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()

def clean(text):
  text = text.lower()

  # Canonicalize DSL.
  text = re.sub(r'\bdomainspecific\b', 'domain-specific', text)
  text = re.sub(r'\bdsl\b', 'domain-specific language', text)

  # Remove “'s”.
  text = re.sub(r"'s\b", ' ', text)

  text = ''.join(' ' if c is '-' else c for c in text)
  tokens = word_tokenize(text)
  punc_free = [w for w in tokens if not w in exclude]
  lemmas = [lemma.lemmatize(word) for word in punc_free]
  normalized = [w for w in lemmas if w not in stop]

  return normalized
