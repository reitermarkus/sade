import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import json

from plotly import graph_objs as go
from plotly.offline import init_notebook_mode, iplot
init_notebook_mode(connected=True)


def create_trace(y, name):
  return go.Bar(
    y = y,
    name = name,
    text = str(y),
    textposition = 'auto',
    opacity = 0.6,
  )

def create_layout(title, **options):
  return {
    **{
      'title': title,
      'font': {'family': 'Helvetica', 'size': 16},
      'bargap': 0.1,
      'barmode': 'group',
      'showlegend': True,
    },
    **options,
  }

def create_fig(title, group_a_data, group_b_data):
  trace_int_del_keys_a = create_trace([group_a_data], 'Group A')
  trace_int_del_keys_b = create_trace([group_b_data], 'Group B')
  data = [trace_int_del_keys_a, trace_int_del_keys_b]
  layout = create_layout(title, xaxis = dict(showticklabels=False,),showlegend=True)
  
  return go.Figure(data = data, layout = layout)

def sum_of_keys(keys):
  return np.array(keys.values).sum()

def read_json(path):
  with open(path, 'r', encoding='utf-8') as f:
    return json.load(f)

def get_tasks(df, group_name, dsl):
  group = df.loc[df['group'] == group_name]
  return group.loc[group['name'].str.contains(f'({dsl})')]

def get_group_data(df, group):
  return {
    'data_frame': df.loc[analysis['group'] == 'a'],
    'int_del_keys': get_tasks(df, group, 'internal')['delete_key_presses'],
    'int_tab_keys': get_tasks(df, group, 'internal')['tab_key_presses'],
    'int_space_keys': get_tasks(df, group, 'internal')['space_key_presses'],
    'ext_del_keys': get_tasks(df, group, 'external')['delete_key_presses'],
    'ext_tab_keys': get_tasks(df, group, 'external')['tab_key_presses'],
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

fig_int_del_keys = create_fig('Delete Keys', 
                              sum_of_keys(group_a['int_del_keys']), 
                              sum_of_keys(group_b['int_del_keys']))

fig_int_tab_keys = create_fig('Tab Keys', 
                              sum_of_keys(group_a['int_tab_keys']), 
                              sum_of_keys(group_b['int_tab_keys']))
                              
fig_int_space_keys = create_fig('Space Keys', 
                              sum_of_keys(group_a['int_space_keys']), 
                              sum_of_keys(group_b['int_space_keys']))