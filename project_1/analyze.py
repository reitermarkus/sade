#!/usr/bin/env python3

from common import *
from repo import Repo
import numpy as np
import pygount

MIN_LOC = 1_000_000

def analyze(repo):
  extensions = LANGUAGES[repo['language']]['extensions']

  r = Repo(repo['owner'], repo['name'], default_branch = repo['default_branch'], language = repo['language'], extensions = extensions)

  json_path = f'{r.path}.json'

  if os.path.isfile(json_path):
    repo = read_json(json_path)
    return repo

  repo['code'], repo['documentation'], repo['empty'] = (0, 0, 0)

  with r:
    for f in r.files:
      # Ignore symlinks.
      if not os.path.isfile(f):
        continue

      analysis = pygount.source_analysis(f, repo['language'], encoding = 'utf-8')

      if analysis.state == 'analyzed':
        repo['code']          += analysis.code + analysis.string
        repo['documentation'] += analysis.documentation
        repo['empty']         += analysis.empty

  write_json(json_path, repo)

  return repo

if __name__ == '__main__':
  for language in LANGUAGES:
    print(f'Analyzing {language}:')

    repos = read_json(f'{SEARCH_PATH}/{language}.json')

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

    write_json(f'{ANALYSIS_PATH}/{language}.json', analyzed_repos)
