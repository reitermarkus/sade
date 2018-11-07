import os
import urllib.request
import tarfile
import shutil
import glob

CACHE_DIR = 'cache'

class Repo:
  def __init__(self, user, repo, language = None, extensions = []):
    self.user = user
    self.repo = repo
    self.language = language
    self.extensions = extensions
    self.path = f'{CACHE_DIR}/{self.user}/{self.repo}'

  def download(self):
    if not os.path.isdir(f'{CACHE_DIR}/{self.user}'):
      os.makedirs(f'{CACHE_DIR}/{self.user}')

    file = f'{CACHE_DIR}/{self.user}/{self.repo}.tgz'

    if os.path.isfile(file):
      print(f'{self.user}/{self.repo} already downloaded.')
      return self

    print(f'Downloading {self.user}/{self.repo} …')
    urllib.request.urlretrieve(f'https://github.com/{self.user}/{self.repo}/archive/master.tar.gz', file)

    return self

  def relevant_files(self, tar):
    for tarinfo in tar:
      ext = os.path.splitext(tarinfo.name)[1]
      if not self.extensions or any(ext == e for e in self.extensions):
        yield tarinfo

  def open(self):
    if os.path.isdir(f'{CACHE_DIR}/{self.user}/{self.repo}'):
      return self

    with tarfile.open(f'{CACHE_DIR}/{self.user}/{self.repo}.tgz') as tar:
      tar.extractall(f'{CACHE_DIR}/{self.user}', members = self.relevant_files(tar))
      os.rename(f'{CACHE_DIR}/{self.user}/{self.repo}-master', f'{CACHE_DIR}/{self.user}/{self.repo}')

    self.files = [f for f in glob.glob(f'{CACHE_DIR}/{self.user}/{self.repo}/**/*') if os.path.isfile(f)]

    return self

  def close(self):
    shutil.rmtree(f'{CACHE_DIR}/{self.user}/{self.repo}')

    self.files = None

    return self

  def __enter__(self):
    self.download()
    self.open()
    return self

  def __exit__(self, *args):
    self.close()
    return self
