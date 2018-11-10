import os
import urllib.request
import tarfile
import shutil
import glob

CACHE_DIR = os.path.expanduser('~/.cache/github_repo_cache')

class Repo:
  def __init__(self, owner, repo, default_branch = 'master', language = None, extensions = []):
    self.owner = owner
    self.repo = repo
    self.name = f'{owner}/{repo}'
    self.language = language
    self.extensions = extensions
    self.default_branch = default_branch
    self.path = f'{CACHE_DIR}/{self.owner}/{self.repo}'

  def download(self):
    if not os.path.isdir(f'{CACHE_DIR}/{self.owner}'):
      os.makedirs(f'{CACHE_DIR}/{self.owner}')

    file = f'{CACHE_DIR}/{self.owner}/{self.repo}.tgz'

    if os.path.isfile(file):
      print(f'{self.owner}/{self.repo} already downloaded.')
      return self

    print(f'Downloading {self.owner}/{self.repo} …')
    urllib.request.urlretrieve(f'https://github.com/{self.owner}/{self.repo}/archive/{self.default_branch}.tar.gz', file)

    return self

  def relevant_files(self, tar):
    for tarinfo in tar:
      ext = os.path.splitext(tarinfo.name)[1]
      if not self.extensions or any(ext == e for e in self.extensions):
        yield tarinfo

  def open(self):
    if os.path.isdir(f'{CACHE_DIR}/{self.owner}/{self.repo}'):
      return self

    with tarfile.open(f'{CACHE_DIR}/{self.owner}/{self.repo}.tgz') as tar:
      tar.extractall(f'{CACHE_DIR}/{self.owner}', members = self.relevant_files(tar))

      if os.path.isdir(f'{CACHE_DIR}/{self.owner}/{self.repo}-{self.default_branch}'):
        os.rename(f'{CACHE_DIR}/{self.owner}/{self.repo}-{self.default_branch}', f'{CACHE_DIR}/{self.owner}/{self.repo}')
      else:
        os.makedirs(f'{CACHE_DIR}/{self.owner}/{self.repo}')

    self.files = [f for f in glob.glob(f'{CACHE_DIR}/{self.owner}/{self.repo}/**/*') if os.path.isfile(f)]

    return self

  def close(self):
    shutil.rmtree(f'{CACHE_DIR}/{self.owner}/{self.repo}')

    self.files = None

    return self

  def __enter__(self):
    self.download()
    self.open()
    return self

  def __exit__(self, *args):
    self.close()
    return self
