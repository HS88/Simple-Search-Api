from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth
import simplejson as Json
import urllib
import urllib2
import wikipedia
from operator import itemgetter
import itertools

import itertools

def compare(string1, string2):
    if len(string2) < len(string1):
        string1, string2 = string2, string1
    n_diff = 0
    for c1, c2 in itertools.izip(string1, string2):
        if c1 != c2:
            n_diff += 1
    delta = len(string2) - len(string1)
    n_diff += delta
    return n_diff


def api_search(query, max_results):
  youtube_result = youtube_search(query, max_results*2)
  bing_result = bing_search(query, max_results*2)
  wikipedia_result = wikipedia_search(query, max_results*2)
  complete_list = youtube_result + bing_result + wikipedia_result
  max_score = 0
  for item in complete_list:
    if(item['score'] > max_score):
      max_score = item['score']

  for item in complete_list:
    item['score'] = item['score'] / max_score
    item['score'] = int((item['score'] * 1000) + 0.05) / 1000.0

  return sorted(complete_list, key=itemgetter('score'), reverse=True)[:max_results]


def find_score(query, title):
    query_words = query.lower().split(" ")
    title_words = title.encode('utf8').lower().split(" ")
    words_count = len(title_words)
    match_word = 0.0
    words_left = float(len(query_words))
    for t_word in title_words:
        for q_word in query_words:
            diff = compare(t_word,q_word)
            if diff == 0:
              match_word = match_word + 1
              words_left = words_left - 1
              break
            else:
              if diff < 3:
                match_word = match_word + 1
                words_left = words_left - 0.8
                break
    final_Score = ((match_word/float(words_count)) - (words_left/float(words_count)))
    return final_Score

def youtube_search(query, max_results):
  testing = []
  youtube = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION,developerKey=settings.DEVELOPER_KEY)
  search_response = youtube.search().list(q=query,part="id,snippet",maxResults=max_results).execute()
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      temp = {}
      temp['url'] = "www.youtube.com/watch?v="+search_result["id"]["videoId"]
      temp['title'] =  search_result["snippet"]["title"]
      temp['source'] = 'Youtube'
      temp['score'] = find_score(query,temp['title'])
      testing.append(temp)
  return testing


def wikipedia_search(query, max_results):
    testing = []
    base_url = 'https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch='+query+'&format=json&=snippet&prop=info&inprop=url&gsrlimit='+str(max_results)
    try:
      response_data = requests.get(base_url).json()
      for item in response_data["query"]["pages"]:
        temp = {}
        temp['url'] = response_data["query"]["pages"][item]["fullurl"]
        temp['title'] = response_data["query"]["pages"][item]["title"]
        temp['source'] = 'Wikipedia'
        temp['score'] = find_score(query,temp['title'])
        testing.append(temp)  
    except Exception as e:
      ""
    return testing


def bing_search(query, max_results, source_type = "Web", format = 'json'):
    testing = []
    query_data = '%27' + urllib.quote(query) + '%27'
    base_url = 'https://api.datamarket.azure.com/Bing/SearchWeb/' + source_type
    url = base_url + '?Query=' + query_data + '&$top=' + str(max_results) + '&$format=' + format    
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36"
    auth = HTTPBasicAuth(settings.BING_KEY, settings.BING_KEY)
    headers = {'User-Agent': user_agent}
    response_data = requests.get(url, headers=headers, auth = auth)
    res = response_data.json()['d']['results']
    for item in res:
      temp = {}
      temp['url']=item['Url']
      temp['title'] = item['Title']
      temp['source'] = 'Bing'
      temp['score'] = find_score(query,temp['title'])
      testing.append(temp)
    return testing