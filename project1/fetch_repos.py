from github import Github, GithubException
from datetime import datetime
from languages import LANGUAGES
from repo import Repo
import numpy as np
import os
import pygount
import time


access_token = os.environ['GITHUB_API_TOKEN']
user = Github(access_token)


def check_rate_limit(lower_limit=10):
  rate_limit = user.get_rate_limit()
  remaining = rate_limit.search.remaining

  if remaining > lower_limit:
    return

  reset_time = rate_limit.search.reset
  now = datetime.utcnow()

  if now < reset_time:
    sleep_time = (now - reset_time).total_seconds()
    print(f'Waiting {sleep_time} seconds for rate limit reset.')
    time.sleep(sleep_time)


def analyze(r):
  check_rate_limit()

  extensions = [LANGUAGES[lang]['extensions'] for lang in LANGUAGES if LANGUAGES[lang]['name'] == r.language][0]

  with Repo(r.owner.login, r.name, r.language, extensions) as repo:
    analysis = [pygount.source_analysis(file, repo.language) for file in repo.files]
    analysis = [a for a in analysis if a.state == 'analyzed']

    analysis = [
      np.array([a.code + a.string, a.documentation, a.empty])
      for a in analysis
    ]

    info = {
      'repo': repo.repo,
      'language': repo.language
    }

    info['code'], info['documentation'], info['empty'] = tuple(sum(analysis))

    print(info)


def search(language, stars, forks, sort_by, order):
  repos = user.search_repositories(f'language:{language}', sort_by, order, stars=stars, forks=forks, created=">=2018-11-01")
  return [analyze(repo) for repo in repos]


if __name__ == '__main__':
  try:
    [search(LANGUAGES[language]['name'], '>=10', '>=10', 'stars', 'desc') for language in LANGUAGES]
  except GithubException as e:
    print(e)
  except KeyboardInterrupt as e:
    print('Search cancelled.')
