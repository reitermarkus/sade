#!/usr/bin/env python3

from languages import LANGUAGES
from repo import Repo
import numpy as np
import pygount

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