#!/usr/bin/env python3

from repo import Repo

import time
import pygount
import os
import glob
import numpy as np

with Repo('reitermarkus', 'sade', language = 'python', extensions = ['.py', '.ipynb']) as repo:
  analysis = [pygount.source_analysis(file, repo.language) for file in repo.files]
  analysis = [a for a in analysis if a.state == 'analyzed']

  analysis = [
    np.array([a.code + a.string, a.documentation, a.empty])
    for a in analysis
  ]

  print(sum(analysis))
