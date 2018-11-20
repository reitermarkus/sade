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
  return go.Layout(
    title = title,
    font = {'family': 'Helvetica', 'size': 16},
    bargap = 0.1,
    barmode = 'group',
    showlegend = False,
    **options,
  )

for path in paths:
  analysis.extend(read_json(path))

analysis_df = pd.DataFrame(data = analysis)

# Sum of all comments
code_comments_sum = analysis_df.groupby(['language']) \
  .agg({'documentation': 'sum', 'code': 'sum'}) \
  .reset_index() \
  .sort_values(by='documentation', ascending = False)

# Chart: sum of all comments
trace = go.Bar(
  x = code_comments_sum['language'],
  y = code_comments_sum['documentation'],
)

layout = create_layout('Lines of Comments per Language<br>(Total for Top 1000 Repositories per Language)')

fig_all_comments = go.Figure(data = [trace], layout = layout)

# Chart: sum of all LOC
trace = go.Bar(
  x = code_comments_sum['language'],
  y = code_comments_sum.sort_values(by = ['code'], ascending = False)['code'],
)

layout = create_layout('Lines of Code of per Language (excluding Empty Lines)<br>(Total for Top 1000 Repositories per Language)')

fig_all_loc = go.Figure(data = [trace], layout = layout)

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
    layout = create_layout(title, yaxis = {
      'tickformat': ',.0%',
      'range': [0,1],
    }),
  )

fig_interpreted = make_figure('Python  vs.  Ruby', ['ruby', 'python'])
fig_system = make_figure('C  vs.  C++  vs.  Rust', ['c', 'c++', 'rust'])
fig_jvm = make_figure('Java  vs.  Kotlin', ['java', 'kotlin'])
fig_functional = make_figure('Ocaml  vs.  Haskell', ['haskell', 'ocaml'])
