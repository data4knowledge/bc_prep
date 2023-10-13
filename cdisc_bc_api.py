import os
import re
import requests
import yaml
import json
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
      self.package_metadata[collection] = self._get_package_metadata(collection)
      self.package_items[collection] = self._get_package_items(collection)
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
      packages = response['_links']['packages']
      return packages
    except:
      print("CDISC BC Library FAILED: %s" % api_url)
      return {}

  def _get_package_items(self, collection) -> dict:
    links_key = {self.GENERIC: 'biomedicalConcepts', self.SDTM: 'datasetSpecializations'}
    results = {}
    try:
      for package in self.package_metadata[collection]:
        api_url = self._url(package['href']) 
        print("CDISC BC Library: %s" % api_url)
        raw = requests.get(api_url, headers=self.headers)
        response = raw.json()
        # if collection == self.__class__.SDTM:
        #   print(f"RESP: {response}")
        for item in response['_links'][links_key[collection]]:
          results[item['title'].upper()] = item
      return results
    except:
      results = {}

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
print("Processing ...")
for collection in [cdisc_library.GENERIC, cdisc_library.SDTM]:
  print(f"Collection: {collection}")
  names = cdisc_library.catalogue(collection)
  for name in names:
    if name == "SYSTOLIC BLOOD PRESSURE":
      print(f"- {name}")
      data = cdisc_library.to_cdisc_json(name, collection)
      if data:
        filename = name.lower().replace(" ", "_")
        filename = re.sub('[^0-9a-zA-Z_]', '-', filename)
        print(f"- {collection}-{name} --> {filename}.yaml & .json")
        with open(f'example_data/cdisc/{collection.lower()}/{filename}.json', 'w') as file:
          json.dump(data, file, ensure_ascii=False, indent=4)
  print("\n\n")
print("Done")
