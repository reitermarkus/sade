#!/usr/bin/env python3

from common import check_rate_limit, write_to_json, SEARCH_PATH
from datetime import datetime
from github import Github, RateLimitExceededException
from languages import LANGUAGES
import os
import time

access_token = os.environ['GITHUB_TOKEN']
user = Github(access_token)
user.per_page = 100

BLACKLIST = [
  'deepfakes/faceswap' # Can only be downloaded when logged into GitHub.
]

def check_rate_limit():
  rate_limit = user.get_rate_limit()
  remaining = rate_limit.search.remaining

  if remaining > 0:
    return

  reset_time = rate_limit.search.reset
  now = datetime.utcnow()

  if now < reset_time:
    sleep_time = (reset_time - now).total_seconds()
    from math import ceil
    print(f'=> Waiting {ceil(sleep_time)} seconds for rate limit reset.')
    time.sleep(sleep_time)


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
      if i == 10:
        if len(repo_list) < total:
          print(f'=> there are some some missing repos: {len(repo_list)}/{total}')
        break
        
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
      print(f"Searching {LANGUAGES[language]['name']}:")
      repos = search(language)
      write_to_json(SEARCH_PATH, repos, language)
  except KeyboardInterrupt as e:
    print('Search cancelled.')
