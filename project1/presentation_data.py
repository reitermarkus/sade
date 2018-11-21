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

def create_pie(df, title, marker, domain):
  labels = df['language']
  values = df['documentation'] / df['documentation'].sum()
  fig = {
        'values': values,
        'labels': labels,
        'name' : title,
        'hole': .25,
        'type': 'pie',
        'marker': marker,
        'domain': domain,
        'hoverinfo': 'label+percent+name'    
      }

  return fig

summary_pie = {}
summary_pie['data'] = []
summary_pie['data'].append(create_pie(select_data(['ruby', 'python']),  'Interpreted', 
                                  {'colors': ['rgb(106, 154, 232)', 'rgb(106, 232, 164)']},
                                  {'x': [0, .48],'y': [.51, 1]}))
summary_pie['data'].append(create_pie(select_data(['c', 'c++', 'rust']),  'System Level', 
                                  {'colors': ['rgb(242, 96, 196)', 'rgb(95, 241, 103)', 'rgb(239, 186, 79)']},
                                  {'x': [0.5, 1],'y': [0, .49]}))
summary_pie['data'].append(create_pie(select_data(['java', 'kotlin']),  'JVM', 
                                  {'colors': ['rgb(247, 131, 123)', 'rgb(165, 247, 243)']},
                                  {'x': [0.5, 1],'y': [.51, 1]}))
summary_pie['data'].append(create_pie(select_data(['haskell', 'ocaml']), 'Functional', 
                                  {'colors': ['rgb(167, 31, 209)', 'rgb(129, 180, 179)']},
                                  {'x': [0, .48],'y': [0, .49]}))
summary_pie['layout'] = {'title': '<b>Summary<b>', 'font': {'family': 'Helvetica', 'size': 14}, 'annotations' : [
            {
                'showarrow': False,
                'text': 'JVM',
                'x': 0.82, 'y': 1.1
            },
            {
                'showarrow': False,
                'text': 'Functional',
                'x': 0.18, 'y': -0.1
            },
            {
                'showarrow': False,
                'text': 'Interpreted',
                'x': 0.2, 'y': 1.1
            },
            {
                'showarrow': False,
                'text': 'System Level',
                'x': 0.84, 'y': -0.1
            }
        ]}
