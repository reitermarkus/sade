import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import json

from plotly import graph_objs as go
from plotly.offline import init_notebook_mode, iplot
init_notebook_mode(connected=True)


def create_trace(y, name, x=[''], showtext=False):
  return go.Bar(
    x = x,
    y = [y],
    name = name,
    text = name if showtext else str(y),
    textposition = 'auto',
    opacity = 0.6,
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
    'ext_space_keys': get_tasks(df, group, 'external')['space_key_presses']
  }

analysis_group_a = pd.DataFrame(data=read_json('./analysis_group_a.json'))
analysis_group_b = pd.DataFrame(data=read_json('./analysis_group_b.json'))

analysis_group_a['group'] = 'a'
analysis_group_b['group'] = 'b'

analysis = pd.concat([analysis_group_a, analysis_group_b])
analysis.dropna(inplace=True)

group_a = get_group_data(analysis, 'a')
group_b = get_group_data(analysis, 'b')


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
  Group A internal vs external figures
'''
fig_int_vs_ext_del_keys_a = create_fig('Group A: Delete Keys', 
                              group_a['int_del_keys'].sum(), 
                              group_a['ext_del_keys'].sum(),
                              ['internal', 'external'])

fig_int_vs_ext_tab_keys_a = create_fig('Group A: Tab Keys', 
                              group_a['int_tab_keys'].sum(), 
                              group_a['ext_tab_keys'].sum(),
                              ['internal', 'external'])
                              
fig_int_vs_ext_space_keys_a = create_fig('Group A: Space Keys', 
                              group_a['int_space_keys'].sum(), 
                              group_a['ext_space_keys'].sum(),
                              ['internal', 'external'])


'''
  Group B internal vs external figures
'''
fig_int_vs_ext_del_keys_b = create_fig('Group B: Delete Keys', 
                              group_b['int_del_keys'].sum(), 
                              group_b['ext_del_keys'].sum(),
                              ['internal', 'external'])

fig_int_vs_ext_tab_keys_b = create_fig('Group B: Tab Keys', 
                              group_b['int_tab_keys'].sum(), 
                              group_b['ext_tab_keys'].sum(),
                              ['internal', 'external'])
                              
fig_int_vs_ext_space_keys_b = create_fig('Group B: Space Keys', 
                              group_b['int_space_keys'].sum(), 
                              group_b['ext_space_keys'].sum(),
                              ['internal', 'external'])
