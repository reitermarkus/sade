#!/usr/bin/env python3

from common import *
from repo import Repo
import numpy as np
import json
import pygount

MIN_LOC = 10_000

def analyze(repo):
  extensions = LANGUAGES[repo['language']]['extensions']

  with Repo(repo['owner'], repo['name'], default_branch = repo['default_branch'], language = repo['language'], extensions = extensions) as r:
    analysis = [pygount.source_analysis(file, repo['language']) for file in r.files]
    analysis = [a for a in analysis if a.state == 'analyzed']

    if analysis:
      analysis = [
        np.array([a.code + a.string, a.documentation, a.empty])
        for a in analysis
      ]
    else:
      analysis = [np.array([0, 0, 0])]

    repo['code'],repo['documentation'], repo['empty'] = tuple(sum(analysis).tolist())

  return repo

if __name__ == '__main__':
  for language in LANGUAGES:
    try:
      print(f'Analyzing {language}:')
      with open(f'{SEARCH_PATH}/{language}.json', 'r', encoding='utf-8') as f:
        repos = json.load(f)

        analyzed_repos = []
        loc = 0

        i = 0

        for repo in repos:
          analysis = analyze(repo)

          analyzed_repos.append(analysis)
          loc += (analysis['code'] + analysis['documentation'] + analysis['empty'])

          i += 1

          print(f'{loc} LOC ({i}/{len(repos)})')

          if loc >= MIN_LOC:
            break
    except FileNotFoundError:
      print(f'File not found: {language}.json')
      continue
    except EOFError:
      continue

    write_to_json(ANALYSIS_PATH, analyzed_repos, language)
