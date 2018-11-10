#!/usr/bin/env python3

from github import Github, GithubException, RateLimitExceededException
from datetime import datetime
from languages import LANGUAGES
from repo import Repo
import numpy as np
import json
import os
import pygount
import time

access_token = os.environ['GITHUB_TOKEN']
user = Github(access_token)
user.per_page = 100

BLACKLIST = [
  'deepfakes/faceswap' # Can only be downloaded when logged into GitHub.
]

MIN_LOC = 1_000_000

REPOS_PATH = 'data/repos'

def check_rate_limit():
  rate_limit = user.get_rate_limit()
  remaining = rate_limit.search.remaining

  if remaining > 0:
    return

  reset_time = rate_limit.search.reset
  now = datetime.utcnow()

  if now < reset_time:
    sleep_time = (reset_time - now).total_seconds()
    print(f'Waiting {sleep_time} seconds for rate limit reset.')
    time.sleep(sleep_time)

def write_to_json(repo_data, language):
  if not os.path.isdir(REPOS_PATH):
    os.makedirs(REPOS_PATH)

  path = f'{REPOS_PATH}/{language}.json'

  if not os.path.exists(path):
    with open(path, mode='w', encoding='utf-8') as f:
      f.write('[]')

  with open(path, mode='w+', encoding='utf-8') as f:
    json.dump(repo_data, f, sort_keys = True, indent = 2)

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

    repo['code'] = int(tuple(sum(analysis))[0])
    repo['documentation'] = int(tuple(sum(analysis))[1])
    repo['empty'] = int(tuple(sum(analysis))[2])
  return repo

def search(language):
  while True:
    try:
      repos = user.search_repositories(f'language:{language}', 'stars', 'desc')
      total = repos.totalCount
      break
    except RateLimitExceededException:
      check_rate_limit()
      continue

  repo_list = []
  i = 0

  while len(repo_list) < total:
    try:
      repo_list.extend([
        {
          'owner': r.owner.login,
          'name': r.name,
          'language': language,
          'stars': r.stargazers_count,
          'forks': r.forks_count,
          'default_branch': r.default_branch,
        }
        for r in repos.get_page(i)
      ])
      print(f'  {len(repo_list)}/{total}')
      i += 1
    except RateLimitExceededException:
      check_rate_limit()
      continue

  repo_list = [repo for repo in repo_list if not f"{repo['owner']}/{repo['name']}" in BLACKLIST]

  return repo_list

if __name__ == '__main__':
  try:
    for language in LANGUAGES:
      print(f'Searching {language}:')
      repos = search(language)

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

      write_to_json(analyzed_repos, language)
  except KeyboardInterrupt as e:
    print('Search cancelled.')
