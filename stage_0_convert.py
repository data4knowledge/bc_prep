import yaml
from utility.utility import *


def process_instances():
  files = files_in_dir('source_data/instances')
  for filename in files:
    with open(filename, "r+") as file:
      instances = yaml.load(file, Loader=yaml.FullLoader)
      new_instances = []
      for instance in instances:
        ignore_file = False
        new_instance = instance
        ident = new_instance['identified_by']
        if not 'has_complex_datatype' in ident:
          ignore_file = True
          continue
        vs = ident['has_complex_datatype'][0]['has_property'][0]
        vs.pop('name')
        vs.pop('question_text')
        vs.pop('prompt_text')
        vs.pop('format')
        ident['data_type'] = [ {'name': "coding", 'value_set': vs['has_coded_value'] }]
        ident.pop('has_complex_datatype', None)
        new_instances.append(new_instance)
        #print(new_instance)
        
        new_items = [x for x in new_instance["has_items"] if x["enabled"]]
        new_instance["has_items"] = new_items
        for item in new_instance["has_items"]:
          if 'has_complex_datatype' in item:
            #print(item['has_complex_datatype'])
            if item['has_complex_datatype'][0]['short_name'] == "PQR":
              vs = item['has_complex_datatype'][0]['has_property'][1]
              vs.pop('name')
              vs.pop('question_text')
              vs.pop('prompt_text')
              vs.pop('format')
              item['data_type'] = [ {'name': "coding", 'value_set': vs['has_coded_value'] }]
              item.pop('has_complex_datatype', None)
              item['data_type'] = [ {'name': "quantity", 'value_set': vs['has_coded_value'] }]
            elif item['has_complex_datatype'][0]['short_name'] == "DATETIME":
              item.pop('has_complex_datatype', None)
              item['data_type'] = [ {'name': "date_time" }]
            elif item['has_complex_datatype'][0]['short_name'] == "CD":
              vs = item['has_complex_datatype'][0]['has_property'][0]
              #print("VS:", vs)
              if 'name' in vs:
                vs.pop('name')
              else:
                vs.pop(':label')
              vs.pop('question_text')
              vs.pop('prompt_text')
              vs.pop('format')
              item['data_type'] = [ {'name': "coding", 'value_set': vs['has_coded_value'] }]
              item.pop('has_complex_datatype', None)
            else:
              print("DATATYPE:", item['has_complex_datatype'][0]['short_name'])
        print(new_instance)
      if not ignore_file:
        file.seek(0)
        yaml.dump(new_instances, file, sort_keys=False)
        file.truncate()

process_instances()                
