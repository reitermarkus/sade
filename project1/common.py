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
      '.C',
      '.cc',
      '.cp',
      '.cxx',
      '.c++',
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

def read_json(path):
  with open(path, 'r', encoding = 'utf-8') as f:
    return json.load(f)

def write_json(path, data):
  directory = os.path.dirname(path)

  if not os.path.isdir(directory):
    os.makedirs(directory)

  with open(path, mode = 'w+', encoding = 'utf-8') as f:
    json.dump(data, f, indent = 2)
