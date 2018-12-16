# /usr/bin/python
import requests
import json

papers_path = '../data/papers.json'

api_endpoint = 'http://ieeexploreapi.ieee.org/api/v1/search/articles'
api_key = '2quujqxvyzwpzztgkud8w2x6'
content_type = "Conferences%2C+Journals+%26+Magazines"
query_text = 'Domain+Specific+Languages'
start_year = '2010'
max_records = 100

url = f'{api_endpoint}?apikey={api_key}&format=json&content_type={content_type}&querytext={query_text}&start_year={start_year}&max_records={max_records}'
res = requests.get(url=url)
data = json.loads(res.text)

with open(papers_path, 'w+', encoding='utf-8') as f:
  json.dump(data, f, indent=2)
