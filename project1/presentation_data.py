import pandas as pd
import numpy as np
import json
import os

from plotly import graph_objs as go

JSON_DIR = 'data/repos/analysis/'
filenames = os.listdir(JSON_DIR)
analysis = []

for filename in filenames:
  with open(f'{JSON_DIR}/{filename}', 'r', encoding = 'utf-8') as f:
    analysis.extend(json.load(f))


analysis_df = pd.DataFrame(data = analysis)


# Sum of all comments
code_comments_sum = analysis_df.groupby(['language']) \
  .agg({'documentation': 'sum', 'code': 'sum'}) \
  .reset_index() \
  .sort_values(by='documentation', ascending=False)

# DataFrame for each language type
functional_df = code_comments_sum[(code_comments_sum['language'] == 'haskell') | \
                         (code_comments_sum['language'] == 'ocaml')]

interpreted_df = code_comments_sum[(code_comments_sum['language'] == 'ruby') | \
                          (code_comments_sum['language'] == 'python')]

jvm_df = code_comments_sum[(code_comments_sum['language'] == 'java') | \
                  (code_comments_sum['language'] == 'kotlin')]

system_level_df = code_comments_sum[(code_comments_sum['language'] == 'c') | \
                                    (code_comments_sum['language'] == 'c++') | \
                                    (code_comments_sum['language'] == 'rust')]

# Chart: sum of all comments
trace = go.Bar(
  x = code_comments_sum['language'],
  y = code_comments_sum['documentation'],
)

layout = go.Layout(
  title  = 'Comments of all languages',
  font   = dict(family = 'Helvetica', size = 16),
  bargap = 0.1
)

fig_all_comments = go.Figure(data = [trace], layout = layout)


# Chart: sum of all LOC
trace = go.Bar(
  x = code_comments_sum['language'],
  y = code_comments_sum.sort_values(by = ['code'], ascending=False)['code'],
)

layout = go.Layout(
  title  = 'Line of codes of all languages <br>(excl. comments and empty lines)',
  font   = dict(family = 'Helvetica', size = 16),
  bargap = 0.1
)

fig_all_loc = go.Figure(data = [trace], layout = layout)


# Chart: interpreted languages
trace1 = go.Bar(
  x = interpreted_df['language'],
  y = interpreted_df['code'],
  name = 'LOC',
  text = 'Code',
  textposition = 'auto'
)

trace2 = go.Bar(
  x = interpreted_df['language'],
  y = interpreted_df['documentation'],
  name = 'Comments',
  text = 'Comments',
  textposition = 'auto'
)

layout = go.Layout(
  title   = 'Python  vs.  Ruby',  
  barmode = 'group',
  font    = dict(family = 'Helvetica', size = 16),
  showlegend = False
)

fig_interpreted = go.Figure(data = [trace1, trace2], layout = layout)


# Chart: system level languages
trace1 = go.Bar(
  x = system_level_df['language'],
  y = system_level_df['code'],
  name = 'LOC',
  text = 'Code',
  textposition = 'auto'
)

trace2 = go.Bar(
  x = system_level_df['language'],
  y = system_level_df['documentation'],
  name = 'Comments',
  text = 'Comments',
  textposition = 'auto'
)

layout = go.Layout(
  title   = 'C  vs.  C++  vs.  Rust',  
  barmode = 'group',
  font    = dict(family = 'Helvetica', size = 16),
  showlegend = False
)

fig_system_level = go.Figure(data = [trace1, trace2], layout = layout)


# Chart: JVM languages
trace1 = go.Bar(
  x = jvm_df['language'],
  y = jvm_df['code'],
  name = 'LOC',
  text = 'Code',
  textposition = 'auto'
)

trace2 = go.Bar(
  x = jvm_df['language'],
  y = jvm_df['documentation'],
  name = 'Comments',
  text = 'Comments',
  textposition = 'auto'
)

layout = go.Layout(
  title   = 'Java  vs.  Kotlin',  
  barmode = 'group',
  font    = dict(family = 'Helvetica', size = 16),
  showlegend = False
)

fig_jvm = go.Figure(data = [trace1, trace2], layout = layout)


# Chart: functional languages
trace1 = go.Bar(
  x = functional_df['language'],
  y = functional_df['code'],
  name = 'LOC',
  text = 'Code',
  textposition = 'auto'
)

trace2 = go.Bar(
  x = functional_df['language'],
  y = functional_df['documentation'],
  name = 'Comments',
  text = 'Comments',
  textposition = 'auto'
)

layout = go.Layout(
  title   = 'Ocaml  vs.  Haskell',  
  barmode = 'group',
  font    = dict(family = 'Helvetica', size = 16),
  showlegend = False
)

fig_functional = go.Figure(data = [trace1, trace2], layout = layout)
