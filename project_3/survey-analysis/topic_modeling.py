import numpy as np
import gensim
import pickle
import pyLDAvis
import pyLDAvis.gensim

from common import clean, oe_questions, stemmer, survey_df
from gensim import corpora
from gensim.models.ldamodel import LdaModel


def create_dir(path, name):
  import os

  if not os.path.exists(f'{path}/{name}'):
    try:
      os.makedirs(f'{path}/{name}')
      return f'{path}/{name}'
    except OSError as e:
      print(e)
      exit()

  return f'{path}/{name}'


def plot_ce_question_stats(question):
  from plotly.offline import init_notebook_mode, iplot
  init_notebook_mode(connected=True)

  labels = survey_df[question].value_counts().reset_index().values[:, 0]
  values = survey_df[question].value_counts().reset_index().values[:, 1]

  iplot({
      "data": [{
        "values": values,
        "labels": labels,
        "type": "pie"
        }],
      "layout": {"title": question}
  })


def compute_lda_model(question_id, answers, num_topics=3, passes=50):
  path = f'./data/open-ended'
  path = create_dir(path, question_id)

  dictionary = corpora.Dictionary(answers)
  doc_term_matrix = [dictionary.doc2bow(answ) for answ in answers]

  pickle.dump(doc_term_matrix, open(f'{path}/corpus.pkl', 'wb'))
  dictionary.save(f'{path}/dictionary.gensim')

  lda_model = LdaModel(doc_term_matrix, num_topics=num_topics, id2word=dictionary, passes=passes)
  lda_model.save(f'{path}/model.gensim')


def display_lda_model(path, num_terms=10):
  dictionary = gensim.corpora.Dictionary.load(f'{path}/dictionary.gensim')
  corpus = pickle.load(open(f'{path}/corpus.pkl', 'rb'))

  lda = LdaModel.load(f'{path}/model.gensim')
  lda_display = pyLDAvis.gensim.prepare(lda, corpus, dictionary, R=num_terms)

  return lda_display


for i in oe_questions:
  clean_text = []
  [clean_text.append(clean(answ).split()) for answ in survey_df[oe_questions[i]] if answ is not np.nan]
  compute_lda_model(i, clean_text)
