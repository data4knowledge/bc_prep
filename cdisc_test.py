import os
import re
import requests
import yaml
import json
import traceback
from utility.utility import *

class CDISCBiomedicalConcepts():

  GENERIC = 'generic'
  SDTM = 'sdtm'
  API_ROOT = 'https://api.library.cdisc.org/api/cosmos/v2'    
  API_URLS = {GENERIC: '/mdr/bc/packages', SDTM: '/mdr/specializations/sdtm/packages'}

  def __init__(self):
    self.api_key = os.getenv('CDISC_API_KEY')
    self.headers =  {"Content-Type":"application/json", "api-key": self.api_key}
    self.package_metadata = {}
    self.package_items = {}
    for collection in [self.GENERIC, self.SDTM]:
      self._get_package_metadata(collection)
      self._get_package_items(collection)
    self._bc_responses = {}

  def exists(self, name, collection) -> dict:
    name_uc = name.upper() # Avoid case mismatches
    if name_uc in self.package_items[collection]:
      return self.package_items[collection][name_uc]
    else:
      return None

  def catalogue(self, collection) -> list:
    return list(self.package_items[collection].keys())
  
  def to_cdisc_json(self, name, collection) -> dict:
    metadata = self.exists(name, collection)
    if not metadata:
      return {}
    else:
      return self._get_bc(metadata['href'])

  def _get_package_metadata(self, collection) -> dict:
    api_url = self._url(self.API_URLS[collection])
    print("CDISC BC Library: %s" % api_url)
    try:
      raw = requests.get(api_url, headers=self.headers)
      response = raw.json()
      #print(f"\n\n\nPACKAGE: {collection}\n\n\n{response}\n\n\n")
      self.package_metadata[collection] = response['_links']['packages']
    except:
      print("CDISC BC Library FAILED: %s" % api_url)
      return {}

  def _get_package_items(self, collection) -> dict:
    links_key = {self.GENERIC: 'biomedicalConcepts', self.SDTM: 'datasetSpecializations'}
    try:
      self.package_items[collection] = {}
      for package in self.package_metadata[collection]:
        api_url = self._url(package['href'])
        date = self._get_date(api_url)
        print(f"CDISC BC Library: {api_url} {date}")
        raw = requests.get(api_url, headers=self.headers)
        response = raw.json()
        #print(f"\n\n\nPACKAGE RESP: {collection}\n\n\n{response}\n\n\n")
        for item in response['_links'][links_key[collection]]:
          key = item['title'].upper()
          if key not in self.package_items[collection]:
            self.package_items[collection][key] = {}
          self.package_items[collection][key][date] = item
    except Exception as e:
      print(f"Exception {e}\n{traceback.format_exc()}")

  def _get_date(self, api_url):
    parts = api_url.split('/')
    return parts[-2]

  def _url(self, relative_url) -> str:
    return "%s%s" % (self.__class__.API_ROOT, relative_url)

  def _get_bc(self, url) -> dict:
    if url in self._bc_responses:
      return self._bc_responses[url]
    else:
      api_url = self._url(url)
      raw = requests.get(api_url, headers=self.headers)
      result = raw.json()
      self._bc_responses[url] = result
      return result

cdisc_library = CDISCBiomedicalConcepts()
print(f"\n\n\n\nPACKAGES:\n{cdisc_library.package_metadata}")
print(f"\n\n\n\nPACKAGE ITEMS:\n{cdisc_library.package_items}")
