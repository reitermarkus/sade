#!/usr/bin/env python3

import json
import os

DATA_DIR = 'data'
SEARCH_PATH = f'{DATA_DIR}/repos/search'
ANALYSIS_PATH = f'{DATA_DIR}/repos/analysis'

LANGUAGES = {
  'python': {
    'name': 'Python',
    'extensions': [
      '.py',
    ],
  },
  'ruby': {
    'name': 'Ruby',
    'extensions': [
      '.rb',
    ],
  },
  'rust': {
    'name': 'Rust',
    'extensions': [
      '.rs',
    ],
  },
  'c': {
    'name': 'C',
    'extensions': [
      '.c',
      '.h',
    ],
  },
  'c++': {
    'name': 'C++',
    'extensions': [
      '.cpp',
      '.hpp',
    ],
  },
  'java': {
    'name': 'Java',
    'extensions': [
      '.java',
    ]
  },
  'kotlin': {
    'name': 'Kotlin',
    'extensions': [
      '.kt',
    ]
  },
  'haskell': {
    'name': 'Haskell',
    'extensions': [
      '.hs',
      '.lhs',
    ]
  },
  'ocaml': {
    'name': 'OCaml',
    'extensions': [
      '.ml',
      '.mli',
    ]
  },
}

def write_to_json(directory, repo_data, language):
  if not os.path.isdir(directory):
    os.makedirs(directory)

  path = f'{directory}/{language}.json'

  if not os.path.exists(path):
    with open(path, mode='w', encoding='utf-8') as f:
      f.write('[]')

  with open(path, mode='w+', encoding='utf-8') as f:
    json.dump(repo_data, f, indent = 2)
