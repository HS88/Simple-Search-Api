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


def api_search(query, max_results):
  youtube_result = youtube_search(query, max_results)
  bing_result = bing_search(query, max_results)
  wikipedia_result = wikipedia_search(query, max_results)
  return youtube_result + bing_result + wikipedia_result

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
        testing.append(temp)  
    except e:
      ""
    return testing


def bing_search(query, max_results, source_type = "Web", top = 2, format = 'json'):
    testing = []
    query_data = '%27' + urllib.quote(query) + '%27'
    base_url = 'https://api.datamarket.azure.com/Bing/SearchWeb/' + source_type
    url = base_url + '?Query=' + query_data + '&$top=' + str(top) + '&$format=' + format    
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
      testing.append(temp)
    return testing