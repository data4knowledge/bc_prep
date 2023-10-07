import requests
from utility.service_environment import ServiceEnvironment

class CTService():

  def __init__(self):
    self.__api_url = ServiceEnvironment().get("CT_SERVER_URL")
  
  def match_identifier(self, id_and_value):
    results = self.identifier_reference(id_and_value['conceptId'])
    #print(f"RESULTS: {results}")
    if results:
      for result in results:
        #print(f"RESULT: {id_and_value} v {result['child']}")
        if result['child']['notation'] == id_and_value['value'] and result['child']['identifier'] == id_and_value['conceptId']:
          return {'cl': result['parent']['identifier'], 'cli': id_and_value['conceptId'] }
    return None

  def match_notation(self, term, cl):
    results = self.notation_reference(term)
    #print(f"RESULTS: {results}")
    if results:
      for result in results:
        #print(f"RESULT: {id_and_value} v {result['child']}")
        if result['child']['notation'] == term and result['parent']['identifier'] == cl:
          return {'cl': result['parent']['identifier'], 'cli': result['child']['identifier']}
    return None

  def term_reference(self, cl, cli):
    return self.api_get("v1/codeLists/terms?codeList=%s&term=%s" % (cl, cli))

  def identifier_reference(self, cli):
    return self.api_get("v1/terms?identifier=%s" % (cli))

  def notation_reference(self, notation):
    return self.api_get("v1/terms?notation=%s" % (notation))

  def api_get(self, url):
    headers =  {"Content-Type":"application/json"}
    full_url = "%s%s" % (self.__api_url, url)
    response = requests.get(full_url, headers=headers)
    if response.status_code == 200:
      return response.json()
    else:
      print(response.text)
      return None