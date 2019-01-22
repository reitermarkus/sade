import os

import numpy as np
import gensim
import pickle
import pyLDAvis
import pyLDAvis.gensim

from gensim import corpora
from gensim.models.ldamodel import LdaModel

import pandas as pd

def create_dir(path):
  if not os.path.isdir(path):
    os.makedirs(path)

def compute_lda_model(path, data, num_topics = 3, passes = 100):
  create_dir(path)

  dictionary = corpora.Dictionary(data)
  doc_term_matrix = [dictionary.doc2bow(d) for d in data]

  pickle.dump(doc_term_matrix, open(f'{path}/corpus.pkl', 'wb'))
  dictionary.save(f'{path}/dictionary.gensim')

  lda_model = LdaModel(doc_term_matrix, num_topics = num_topics, id2word = dictionary, passes = passes)
  lda_model.save(f'{path}/model.gensim')

  return lda_model

def display_lda_model(path, num_terms=13):
  dictionary = gensim.corpora.Dictionary.load(f'{path}/dictionary.gensim')
  corpus = pickle.load(open(f'{path}/corpus.pkl', 'rb'))

  lda = LdaModel.load(f'{path}/model.gensim')
  lda_display = pyLDAvis.gensim.prepare(lda, corpus, dictionary, R = num_terms)

  return lda_display
