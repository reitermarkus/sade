import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import pyLDAvis
import pyLDAvis.gensim
import nltk
import string

from plotly import graph_objs as go
from plotly.offline import init_notebook_mode, iplot

from nltk.corpus import opinion_lexicon, stopwords, sentiwordnet as swn
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer


nltk.download('wordnet')
nltk.download('opinion_lexicon')
nltk.download('stopwords')
nltk.download('punkt')

pyLDAvis.enable_notebook()
init_notebook_mode(connected=True)


survey_df = pd.read_csv('./data/MSD Survey.csv')

stemmer = PorterStemmer()


def clean(text):
  # Remove stopwords and punctuation, lemmatize words
  stop = set(stopwords.words('english'))
  exclude = set(string.punctuation)
  lemma = WordNetLemmatizer()

  text = stemmer.stem(text)
  no_stop = ' '.join([i for i in text.lower().split() if i not in stop])
  no_punc = ''.join(ch for ch in no_stop if ch not in exclude)
  cleaned = ' '.join(lemma.lemmatize(word) for word in no_punc.split())

  return cleaned


def plot_ce_question_stats(question):
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


ce_questions = {
  0: "Since how many semesters have you been studying?",
  1: "How many hours per week do you spend on a homework?",
  2: "Are you satisfied with the topics taught in the lecture?",
  3: "Do you intend to use the topics you learned outside of the course? [Descriptive Statistics]",
  4: "Do you intend to use the topics you learned outside of the course? [Data Mining]",
  5: "Do you intend to use the topics you learned outside of the course? [Explorative Analysis]",
  6: "Do you intend to use the topics you learned outside of the course? [Prediction model]",
  7: "Do you intend to use the topics you learned outside of the course? [Natural Language Processing]",
  8: "Do you intend to use the topics you learned outside of the course? [Python]",
  9: "Do you intend to use the topics you learned outside of the course? [Jupyter Notebook]",
  10: "Do you intend to use the topics you learned outside of the course? [Experimentation]",
  11: "Do you intend to use the topics you learned outside of the course? [Surveys]",
  12: "Rate the difficulty of the lecture",
  13: "Would you attend this course again?",
  14: "Would you recommend this course to others?"
}

oe_questions = {
  0: "What do you study?",
  1: "What is your profession?",
  2: "Why did you choose the lecture MSD? ",
  3: "What did you miss in the lecture? ",
  4: "Reflect on the repository mining project (topic selection, were your expectations fulfilled, learnings, etc.)",
  5: "Why do you think that the weekly exercise sheets were a good preparation for the projects or not?",
  6: "What kind of extra material did you use to solve the weekly homeworks and the project?",
  7: "What did you like in the course?",
  8: "What did you not like in the course?",
  9: "How do you agree with the  following statement: The topics taught in the lecture can be applied in various application areas",
  10: "What would you suggest for the improvement of the lecture?"
}
