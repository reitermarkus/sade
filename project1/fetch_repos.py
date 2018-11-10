#!/usr/bin/env python3

from github import Github, GithubException
from datetime import datetime
from languages import LANGUAGES
from repo import Repo
import numpy as np
import os
import pygount
import time

access_token = os.environ['GITHUB_TOKEN']
user = Github(access_token)

MIN_LOC = 1_000_000
loc_counter = 0
min_loc_reached_languages = []

def check_rate_limit():
  rate_limit = user.get_rate_limit()
  remaining = rate_limit.search.remaining

  if remaining > 0:
    return

  reset_time = rate_limit.search.reset
  now = datetime.utcnow()

  if now < reset_time:
    sleep_time = (now - reset_time).total_seconds()
    print(f'Waiting {sleep_time} seconds for rate limit reset.')
    time.sleep(sleep_time)

def check_loc_counter(language, locs_to_add):
  global loc_counter
  loc_counter += locs_to_add

  if loc_counter >= MIN_LOC:
      min_loc_reached_languages.append(language)

def analyze(r, language):
  check_rate_limit()

  if (r.language in min_loc_reached_languages):
    return

  repo_info = {
    'owner': r.owner.login,
    'name': r.name,
    'language': r.language,
    'stars': r.stargazers_count,
    'forks': r.forks_count,
    'default_branch': r.default_branch,
  }

  extensions = LANGUAGES[language]['extensions']

  with Repo(r.owner.login, r.name, default_branch = r.default_branch, language = r.language, extensions = extensions) as repo:
    analysis = [pygount.source_analysis(file, repo.language) for file in repo.files]
    analysis = [a for a in analysis if a.state == 'analyzed']

    if analysis:
      analysis = [
        np.array([a.code + a.string, a.documentation, a.empty])
        for a in analysis
      ]
    else:
      analysis = [np.array([0, 0, 0])]

    repo_info['code'], repo_info['documentation'], repo_info['empty'] = tuple(sum(analysis))

    check_loc_counter(r.language, sum(sum(analysis)))

    print(repo_info)

def search(language):
  repos = user.search_repositories(f'language:{language}', 'stars', 'desc', stars = '>=100', forks = '>=10')
  return [analyze(repo, language) for repo in repos]

if __name__ == '__main__':
  try:
    for language in LANGUAGES:
      print(f'Searching {language}:')
      search(language)
      loc_counter = 0
  except GithubException as e:
    print(e)
  except KeyboardInterrupt as e:
    print('Search cancelled.')
