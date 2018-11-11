#!/usr/bin/env python3

import json
import os

SEARCH_PATH = 'data/repos/search'

def write_to_json(path, repo_data, language):
  if not os.path.isdir(path):
    os.makedirs(path)

  path = f'{path}/{language}.json'

  if not os.path.exists(path):
    with open(path, mode='w', encoding='utf-8') as f:
      f.write('[]')

  with open(path, mode='w+', encoding='utf-8') as f:
    json.dump(repo_data, f, sort_keys = True, indent = 2)
