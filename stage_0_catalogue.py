import yaml
from utility.utility import *

def process_instances():
  files = files_in_dir('source_data/instances')
  bc_catalogue = {}
  print(f"Processing ...")
  for filename in files:
    with open(filename, "r+") as file:
      instances = yaml.load(file, Loader=yaml.FullLoader)
      for instance in instances:
        ident = instance['identified_by']
        if not 'has_complex_datatype' in ident:
          name = instance['name']
          print(f"- {name}")
          identifier = instance['identifier'] if 'identifier' in instance else ''
          c_code = ident['data_type'][0]['value_set'][0]
          bc_catalogue[c_code['cli']] = {'name': name, 'identifier': identifier, 'c_code': c_code}
  with open('source_data/catalogue/catalogue.yaml', 'w') as file:
    yaml.dump(bc_catalogue, file)
  print(f"Done")

process_instances()                
