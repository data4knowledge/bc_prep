import yaml
from utility.utility import *
from utility.ra_service import *
from utility.crm_service import *
from utility.ct_service import *

class Template():

  def __init__(self, template):
    self.definition = template
    self._crm_map = {}
    self._crm_paths = {}
    if "canonical" in template["identified_by"]:
      name = format_name(template["identified_by"]["name"])
      crm_server = CRMService()
      result = crm_server.crm_node_data_types(template["identified_by"]["canonical"])
      self._crm_paths[template["identified_by"]["canonical"]] = result
      self._crm_map[name] = template["identified_by"]["canonical"]
    for item in template["has_items"]: 
      if "canonical" in item:
        name = format_name(item["name"])
        crm_server = CRMService()
        result = crm_server.crm_node_data_types(item["canonical"])
        self._crm_paths[item["canonical"]] = result
        self._crm_map[name] = item["canonical"]

class Templates():

  def __init__(self):
    self.items = {}
    with open("source_data/templates/templates.yaml") as file:
      templates = yaml.load(file, Loader=yaml.FullLoader)
      for template in templates:
        self.items[template['name']] = Template(template)
      

class Specialization():
  
  def __init__(self, definition):
    self.definition = definition
    self.name = definition['shortName']
    self.domain = definition['domain']

  def identifier(self):
    pass


class Specializations():

  def __init__(self):
    self.items = {}
    files = files_in_dir('source_data/cdisc/sdtm')
    for filename in files:
      if not filename.endswith('yaml'):
        continue
      with open(filename, "r+") as file:
        instance = yaml.load(file, Loader=yaml.FullLoader)
        self.items[instance['shortName']] = Specialization(instance)
    
templates = Templates()
for name, template in templates.items.items():
  print(f"Name: {name}")

domain_template_map = {
  'DM': 'Base Observation',
  'VS': 'Base Observation',
  'EG': 'Base Observation',
  'TU': 'Base Observation',
  'PR': 'Base Observation',
  'MB': 'Base Observation',
  'LB': 'Base Laboratory'
}

specializations = Specializations()
for name, specialization in specializations.items.items():
  domain = specialization.domain
  if domain in domain_template_map:
    template = domain_template_map[domain]
  else:
    pass
