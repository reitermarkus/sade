from github import Github, GithubException, BadCredentialsException
import os
import time
from datetime import datetime


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


def repo_details(repo):
  check_rate_limit()

  return {
      'user': repo.owner.login,
      'repo': repo.full_name,
      'language': repo.language,
      'stars': repo.stargazers_count,
      'forks': repo.forks,
      'watchers': repo.watchers,
      'url': repo.url
  }


def search(language, stars, forks, sort_by, order):
  repos = user.search_repositories(f'language:{language}', sort_by, order, stars=stars, forks=forks)
  return [repo_details(repo) for repo in repos]


if __name__ == '__main__':
  try:
    repos = search('python', '>=100', '>=10', 'stars', 'desc')
  except BadCredentialsException as e:
    print(e)
  except GithubException as e:
    print(e)
  except KeyboardInterrupt as e:
    print('Search cancelled.')
