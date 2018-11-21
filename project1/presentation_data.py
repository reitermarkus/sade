import pandas as pd
import numpy as np
import json
import os
import glob

from plotly import graph_objs as go

from common import *

paths = glob.glob('data/repos/analysis/*.json')
analysis = []

def create_layout(title, **options):
  return {
    **{
      'title': title,
      'font': {'family': 'Helvetica', 'size': 16},
      'bargap': 0.1,
      'barmode': 'group',
      'showlegend': False,
      'yaxis': {
        'tickformat': ',.0%',
        'range': [0, 1],
      },
    },
    **options,
  }

for path in paths:
  analysis.extend(read_json(path))

analysis_df = pd.DataFrame(data = analysis)

# Sum of all comments
code_comments_sum = analysis_df.groupby(['language']) \
  .agg({'documentation': 'sum', 'code': 'sum'}) \
  .reset_index() \
  .sort_values(by='documentation', ascending = False)


total = (code_comments_sum['code'] + code_comments_sum['documentation'])

trace = go.Bar(
  x = code_comments_sum['language'],
  y = code_comments_sum['documentation'] / total,
)

layout = create_layout('Percent of Comments per Language', yaxis = {
      'tickformat': ',.0%',
      'range': [0, 0.35],
    })

fig_all_comments = go.Figure(data = [trace], layout = layout)

def select_data(languages):
  return code_comments_sum[code_comments_sum['language'].isin(list(languages))]

def make_traces(data):
  total = (data['code'] + data['documentation'])

  trace1 = go.Bar(
    x = data['language'],
    y = data['code'] / total,
    text = 'Code',
    textposition = 'auto',
  )

  trace2 = go.Bar(
    x = data['language'],
    y = data['documentation'] / total,
    text = 'Comments',
    textposition = 'auto',
  )

  return [trace1, trace2]

def make_figure(title, languages):
  return go.Figure(
    data = make_traces(select_data(languages)),
    layout = create_layout(title),
  )

fig_interpreted = make_figure('Python  vs.  Ruby', ['ruby', 'python'])
fig_system = make_figure('C  vs.  C++  vs.  Rust', ['c', 'c++', 'rust'])
fig_jvm = make_figure('Java  vs.  Kotlin', ['java', 'kotlin'])
fig_functional = make_figure('Ocaml  vs.  Haskell', ['haskell', 'ocaml'])

def create_pie(df, title):
  labels = df['language']
  values = df['documentation'] / df['documentation'].sum()
  fig = {
    "data": [
      {
        "values": values,
        "labels": labels,
        "hole": .4,
        "type": "pie"
      }],
    "layout": {
          "title": title,
      }
  }

  return fig

summary_pie = []
summary_pie.append(create_pie(select_data(['ruby', 'python']),  'Interpreted'))
summary_pie.append(create_pie(select_data(['c', 'c++', 'rust']),  'System Level'))
summary_pie.append(create_pie(select_data(['java', 'kotlin']),  'JVM'))
summary_pie.append(create_pie(select_data(['haskell', 'ocaml']),  'Functional'))

