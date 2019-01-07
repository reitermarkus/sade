#!/usr/bin/env python3

import requests
import json
import urllib

papers_path = 'data/papers.json'

api_endpoint = 'http://ieeexploreapi.ieee.org/api/v1/search/articles'
api_key = '2quujqxvyzwpzztgkud8w2x6'

query_string = urllib.parse.urlencode({
  'apikey': api_key,
  'format': 'json',
  'content_type': 'Conferences, Journals & Magazines',
  'querytext': 'Domain Specific Languages',
  'start_year': 2010,
  'max_records': 100,
})

url = f'{api_endpoint}?{query_string}'
res = requests.get(url=url)
data = json.loads(res.text)

with open(papers_path, 'w+', encoding='utf-8') as f:
  json.dump(data, f, indent=2)
