import re
import yaml
from utility.utility import *
from utility.ra_service import *
from utility.crm_service import *
from utility.ct_service import *
from utility.sdtm_service import *

class Catalogue():

  def __init__(self) -> None:
    with open("source_data/catalogue/catalogue.yaml", "r") as file:
      self.entries = yaml.load(file, Loader=yaml.FullLoader)
    
  def match(self, cli):
    return cli in self.entries

class Template():

  def __init__(self, template):
    self.definition = template
    self._crm_paths = {}
    self.crm_property = {}
    for item in template["has_items"]: 
      if "canonical" in item:
        name = item["name"]
        crm_server = CRMService()
        results = crm_server.crm_node_data_types(item["canonical"])
        if results:
          self.crm_property[name] = {}
          for key, value in results.items():
            self.crm_property[name][value] = key
        for key, value in results.items():
          self._crm_paths[value] = {'name': item["name"], 'data_type_path': key}
    #print(f"\n\nTEMPLATE: {template['name']}")
    #print(f"PATHS: {self.crm_property}")

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
      #print(f"ID: {identifier['assignedTerm']}")
      return identifier['assignedTerm']
    except:
      #print(f"ID: None {self.definition}")
      return None

  def variable(self, name):
    try:
      var = next(item for item in self.definition["variables"] if item["name"] == name)
      #print(f"VAR: {var}")
      return var
    except:
      #print(f"VAR: None {name}")
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

def remove_quantity_datatype(item):
  remove_datatype(item, 'quantity')

def remove_coding_datatype(item):
  remove_datatype(item, 'coding')

def get_filename(name): 
  filename = name.lower().replace(" ", "_")
  filename = re.sub('[^0-9a-zA-Z_]', '-', filename)
  return filename

def remove_datatype(item, name):
  data_types = item['data_type']
  for i in range(len(data_types)):
    if data_types[i]['name'] == name:
        del data_types[i]
        break

print("Processing ...")
catalogue = Catalogue()
templates = Templates()
#for name, template in templates.items.items():
#  print(f"Name: {name}")

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
variable_crm = {}
for domain, entry in domain_template_map.items():
  variable_crm[domain] = {}
  definition = next(item for item in domains['items'] if item["name"] == domain)
  entry['definition'] = sdtm.get_domain(definition['uuid'])
  for variable in entry['definition']['items']:
    for reference in variable['crm_references']:
      variable_crm[domain][reference['uri_reference']] = variable['name']
#print(f"VARIABLE: {variable_crm}")

specializations = Specializations()
ct = CTService()
for name, specialization in specializations.items.items():
  print(f"- BC {name}")
  domain = specialization.domain
  if domain in domain_template_map:
    template_name = domain_template_map[domain]['template']
    identifier = specialization.identifier()
    if identifier:
      if not catalogue.match(identifier['conceptId']):
        template = templates.items[template_name]
        instance = template.definition
        instance['based_on'] = template_name
        ct_ref = ct.match_identifier(identifier)
        if ct_ref:
          instance['name'] = specialization.definition['shortName']
          instance['identified_by']['data_type'][0]['value_set'] = ct_ref
          filename = get_filename(instance['name'])
          for item in instance['has_items']:
            #print(f"ITEM: {item}")
            if item['name'] in template.crm_property:
              #print(f"ITEM NAME")
              for crm_ref in template.crm_property[item['name']]:
                #print(f"CRM REF {crm_ref}")
                if crm_ref in variable_crm[domain]:
                  #print(f"VAR FOUND: {crm_ref} -> {variable_crm[domain][crm_ref]}")
                  var = specialization.variable(variable_crm[domain][crm_ref])
                  if var and 'valueList' in var:
                    var_name = var['name']
                    #print(f"VALUE LIST FOUND: {variable_crm[domain][crm_ref]} with {var['valueList']}")
                    terms = []
                    for term in var['valueList']:
                      ct_result = ct.match_notation(term, var['codelist']['conceptId'])
                      terms.append(ct_result)
                      #print(f"CT RESULT: {ct_result}")
                    item['data_type'][0]['value_set'] = terms
                    if len(item['data_type']) > 1:
                      if var_name.endswith('ORRES'):
                        remove_quantity_datatype(item)
                  elif var:
                    #print(f"VAR: {var}")
                    var_name = var['name']
                    if var_name.endswith('ORRES'):
                      remove_coding_datatype(item)
            else:
              item['enabled'] = False
          with open(f"source_data/instances/cdisc/{filename}.yaml", 'w') as file:
            yaml.dump(instance, file)
      else:
        print(f"  Match found for identifier {identifier} in catalogue")
    else:
      print(f"  Failed to match CT for identifier {identifier}")
  else:
    print(f"  In domain {domain} but not selected for processing")
  print("\n")
print("Done")
