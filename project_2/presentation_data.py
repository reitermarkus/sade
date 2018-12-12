import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import json

from plotly import graph_objs as go
from plotly.offline import init_notebook_mode, iplot
init_notebook_mode(connected=True)

'''
  PLOT METHODS
'''
def create_trace(y, name, x=[''], showtext=False):
  return go.Bar(
    x = x,
    y = [y],
    name = name,
    text = name if showtext else '',
    textposition = 'auto',
  )

def create_layout(title, barmode, **options):
  return {
    **{
      'title': title,
      'font': {'family': 'Helvetica', 'size': 16},
      'bargap': 0.1,
      'barmode': barmode,
      'showlegend': True,
    },
    **options,
  }

def create_vs_fig(title, traces, showlegend=False):
  layout = create_layout(title, 'stack', xaxis = dict(showticklabels=True), showlegend=showlegend)

  return go.Figure(data = traces, layout = layout)

def create_fig(title, group_a_data, group_b_data, trace_name, showticklabels=False):
  trace_keys_a = create_trace(group_a_data, trace_name[0])
  trace_keys_b = create_trace(group_b_data, trace_name[1])
  data = [trace_keys_a, trace_keys_b]
  layout = create_layout(title, 'group', xaxis = dict(showticklabels=showticklabels), showlegend=True)

  return go.Figure(data = data, layout = layout)

def create_percentage_fig(title, keys, group_a, group_b, total_a, total_b, agg_method):
  return {
    'data': [
      create_trace(agg_method(group_a[f'int_{keys}_keys']) / total_a, 'Internal', ['Group A'], True),
      create_trace(agg_method(group_a[f'ext_{keys}_keys']) / total_a, 'External', ['Group A'], True),
      create_trace(agg_method(group_b[f'int_{keys}_keys']) / total_b, 'Internal', ['Group B'], True),
      create_trace(agg_method(group_b[f'ext_{keys}_keys']) / total_b, 'External', ['Group B'], True),
    ], 
    'layout': create_layout(title, 'group', **{
      'yaxis': {
        'tickformat': ',.0%',
        'range': [0, 1],
      }
    }),
  }


'''
  PYTHON HELPER METHODS
'''
def sum_of_keys(keys):
  return keys.sum()

def read_json(path):
  with open(path, 'r', encoding='utf-8') as f:
    return json.load(f)

def get_tasks(df, group_name, dsl):
  group = df.loc[df['group'] == group_name]
  return group.loc[group['name'].str.contains(f'({dsl})')]

def get_group_data(df, group):
  return {
    'data_frame':     df.loc[analysis['group'] == group],
    'int_del_keys':   get_tasks(df, group, 'internal')['delete_key_presses'],
    'int_tab_keys':   get_tasks(df, group, 'internal')['tab_key_presses'],
    'int_space_keys': get_tasks(df, group, 'internal')['space_key_presses'],
    'ext_del_keys':   get_tasks(df, group, 'external')['delete_key_presses'],
    'ext_tab_keys':   get_tasks(df, group, 'external')['tab_key_presses'],
    'ext_space_keys': get_tasks(df, group, 'external')['space_key_presses'],
    'int_typing_speed': get_tasks(df, group, 'internal')['characters_per_minute'],
    'ext_typing_speed': get_tasks(df, group, 'external')['characters_per_minute']
}

'''
  MAIN
'''
analysis_group_a = pd.DataFrame(data=read_json('./data/analysis_group_a.json'))
analysis_group_b = pd.DataFrame(data=read_json('./data/analysis_group_b.json'))

analysis_group_a['group'] = 'a'
analysis_group_b['group'] = 'b'

analysis = pd.concat([analysis_group_a, analysis_group_b])
analysis.dropna(inplace=True)

group_a = get_group_data(analysis, 'a')
group_b = get_group_data(analysis, 'b')


'''
  Group A/B internal vs external percentage 
'''
total_a = group_a['int_del_keys'].sum() + group_a['ext_del_keys'].sum()
total_b = group_b['int_del_keys'].sum() + group_b['ext_del_keys'].sum()
fig_deletions_per_group = create_percentage_fig('Deletions (in % of total deletions per group)', 'del', group_a, group_b, total_a, total_b, np.sum)

total_a = group_a['int_tab_keys'].sum() + group_a['ext_tab_keys'].sum()
total_b = group_b['int_tab_keys'].sum() + group_b['ext_tab_keys'].sum()
fig_tabs_per_group = create_percentage_fig('Tabs (in % of total tabs per group)', 'tab', group_a, group_b, total_a, total_b, np.sum)

total_a = group_a['int_space_keys'].sum() + group_a['ext_space_keys'].sum()
total_b = group_b['int_space_keys'].sum() + group_b['ext_space_keys'].sum()
fig_spaces_per_group = create_percentage_fig('Spaces (in % of total spaces per group)', 'space', group_a, group_b, total_a, total_b, np.sum)


'''
  Group A internal vs Group B internal
'''
traces = [
  create_trace(group_a['int_del_keys'].sum(), 'Group A', ['Delete Keys'], True),
  create_trace(group_b['int_del_keys'].sum(), 'Group B', ['Delete Keys'], True),

  create_trace(group_a['int_tab_keys'].sum(), 'Group A', ['Tab Keys'], True),
  create_trace(group_b['int_tab_keys'].sum(), 'Group B', ['Tab Keys'], True),

  create_trace(group_a['int_space_keys'].sum(), 'Group A', ['Space Keys'], True),
  create_trace(group_b['int_space_keys'].sum(), 'Group B', ['Space Keys'], True),
]

fig_a_vs_b_int = create_vs_fig('Group A vs Group B: Internal', traces)


'''
  Group B external vs Group B external
'''
traces = [
  create_trace(group_a['ext_del_keys'].sum(), 'Group A', ['Delete Keys'], True),
  create_trace(group_b['ext_del_keys'].sum(), 'Group B', ['Delete Keys'], True),

  create_trace(group_a['ext_tab_keys'].sum(), 'Group A', ['Tab Keys'], True),
  create_trace(group_b['ext_tab_keys'].sum(), 'Group B', ['Tab Keys'], True),

  create_trace(group_a['ext_space_keys'].sum(), 'Group A', ['Space Keys'], True),
  create_trace(group_b['ext_space_keys'].sum(), 'Group B', ['Space Keys'], True),
]

fig_a_vs_b_ext = create_vs_fig('Group A vs Group B: External', traces)


'''
  Group A/B median
'''
total_a = group_a['int_del_keys'].median() + group_a['ext_del_keys'].median()
total_b = group_b['int_del_keys'].median() + group_b['ext_del_keys'].median()
fig_median_deletions = create_percentage_fig('Median of total deletions per group', 'del', group_a, group_b, total_a, total_b, np.median)

total_a = group_a['int_tab_keys'].mean() + group_a['ext_tab_keys'].mean()
total_b = group_b['int_tab_keys'].mean() + group_b['ext_tab_keys'].mean()
fig_median_tabs = create_percentage_fig('Median of total tabs per group', 'tab', group_a, group_b, total_a, total_b, np.mean)

total_a = group_a['int_space_keys'].median() + group_a['ext_space_keys'].median()
total_b = group_b['int_space_keys'].median() + group_b['ext_space_keys'].median()
fig_median_spaces = create_percentage_fig('Median of total spaces per group', 'space', group_a, group_b, total_a, total_b, np.median)


def create_percentage_fig_typing_speed(title, group_a, group_b, agg_method):
  return {
    'data': [
      create_trace(agg_method(group_a['int_typing_speed']), 'Internal', ['Group A'], True),
      create_trace(agg_method(group_a['ext_typing_speed']), 'External', ['Group A'], True),
      create_trace(agg_method(group_b['int_typing_speed']), 'Internal', ['Group B'], True),
      create_trace(agg_method(group_b['ext_typing_speed']), 'External', ['Group B'], True),
    ], 
    'layout': create_layout(title, 'group', **{
    }),
  }


'''
  Typing Speed
# '''
fig_median_typing_speed = create_percentage_fig_typing_speed('Median of typing speeds (per minute)', group_a, group_b, np.median)

