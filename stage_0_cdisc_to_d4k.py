import yaml
from utility.utility import *
from utility.ra_service import *
from utility.crm_service import *
from utility.ct_service import *
from utility.sdtm_service import *

class Template():

  def __init__(self, template):
    self.definition = template
    self._crm_paths = {}
    for item in template["has_items"]: 
      if "canonical" in item:
        name = format_name(item["name"])
        crm_server = CRMService()
        results = crm_server.crm_node_data_types(item["canonical"])
        for key, value in results.items():
          self._crm_paths[value] = {'name': item["name"], 'data_type_path': key}
    #print(f"\n\nTEMPLATE: {template['name']}")
    #print(f"PATHS: {self._crm_paths}")

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
    try:
      identifier = next(item for item in self.definition["variables"] if item["name"].endswith("TESTCD"))
      print(f"ID: {identifier['assignedTerm']}")
      return identifier['assignedTerm']
    except:
      print(f"ID: None {self.definition}")
      return None

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
  'DM': {'template': 'Base Observation'},
  'VS': {'template': 'Base Observation'},
  'EG': {'template': 'Base Observation'},
  'TU': {'template': 'Base Observation'},
  'MB': {'template': 'Base Observation'},
  'LB': {'template': 'Base Laboratory'}
}
sdtm = SDTMService()
domains = sdtm.get_domains()
for domain, entry in domain_template_map.items():
  definition = next(item for item in domains['items'] if item["name"] == domain)
  entry['definition'] = sdtm.get_domain(definition['uuid'])
  #print(f"DOMAIN: {entry}")

specializations = Specializations()
ct = CTService()
for name, specialization in specializations.items.items():
  domain = specialization.domain
  if domain in domain_template_map:
    template_name = domain_template_map[domain]['template']
    identifier = specialization.identifier()
    if identifier:
      instance = templates.items[template_name].definition
      instance['based_on'] = template_name
      ct_ref = ct.match_identifier(identifier)
      if ct_ref:
        instance['identified_by']['data_type'][0]['value_set'] = ct_ref
        for item in instance['has_items']:
          pass
        with open(f"source_data/instances/cdisc/{identifier['conceptId']}.yaml", 'w') as file:
          yaml.dump(instance, file)
      else:
        print(f"Failed to match CT for identifier {identifier}")
  else:
    pass
