#!/usr/bin/env python3

from repo import Repo

import pygount
import numpy as np

def main():
  with Repo('reitermarkus', 'sade', language = 'python', extensions = ['.py', '.ipynb']) as repo:
    analysis = [pygount.source_analysis(file, repo.language) for file in repo.files]
    analysis = [a for a in analysis if a.state == 'analyzed']

    analysis = [
      np.array([a.code + a.string, a.documentation, a.empty])
      for a in analysis
    ]

    info = {
      'repo': repo.name,
      'language': repo.language
    }

    info['code'], info['documentation'], info['empty'] = tuple(sum(analysis))

    print(info)

if __name__ == '__main__':
  main()
