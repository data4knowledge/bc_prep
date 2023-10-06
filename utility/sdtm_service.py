import requests
from utility.service_environment import ServiceEnvironment

class SDTMService():

  def __init__(self):
    self.__api_url = ServiceEnvironment().get("SDTM_SERVER_URL")
  
  def get_domains(self):
    return self.api_get("v1/domains")

  def get_domain(self, uuid):
    return self.api_get("v1/domains/%s?expand=true" % (uuid))

  def api_get(self, url):
    headers =  {"Content-Type":"application/json"}
    response = requests.get("%s%s" % (self.__api_url, url), headers=headers)
    #print(response)
    return response.json()