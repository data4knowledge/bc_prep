import yaml
from utility.utility import *

nodes = { "BC_INSTANCE": [], "BC_ITEM": [], "BC_DATA_TYPE": [], "BC_VALUE_SET": [] }
relationships = { "HAS_ITEM": [], "HAS_IDENTIFIER": [], "HAS_QUALIFIER": [], "BC_NARROWER": [], "HAS_DATA_TYPE": [], "HAS_RESPONSE": [] }
bc_uri = {}

def format_name(name):
    name = name.lower()
    name = name.replace(" ", "_")
    return name

def process():
  files = files_in_dir('source_data/instances')
  for filename in files:
    with open(filename) as file:
      narrower = {}
      instances = yaml.load(file, Loader=yaml.FullLoader)
      for instance in instances:
        print(instance)
        print("instance:", instance["name"])
        uri_name = format_name(instance["name"])
        base_uri = "http://id.d4k.dk/dataset/bc_instance/%s" % (uri_name)
        nodes["BC_INSTANCE"].append({"name": instance["name"], "based_on": instance["based_on"], "uri": base_uri})           
        bc_uri[uri_name] = base_uri
        narrower[base_uri] = []
        if "narrower" in instance:
          for children in instance["narrower"]:
            narrower[base_uri].append(format_name(children))
        # Identifier Node and Associated Data Type
        item = instance["identified_by"]
        qualifier_item = ""
        if "qualified_by" in item:
          qualifier_item = item["qualified_by"]
        name = format_name(item["name"])
        item_uri = "%s/%s" % (base_uri, name)
        identifier_uri = item_uri
        collect = False
        if "collect" in item:
          collect = item["collect"]
        print(item)
        record = {
          "name": item["name"], 
          "collect": collect,
          "enabled": item["enabled"],
          "uri": item_uri
        }
        nodes["BC_ITEM"].append(record)
        relationships["HAS_ITEM"].append({"from": base_uri, "to": item_uri})
        relationships["HAS_IDENTIFIER"].append({"from": base_uri, "to": item_uri})
        if "data_type" in item:
          for data_type in item["data_type"]: 
            #print(item["data_type"])
            name = format_name(data_type["name"])
            data_type_uri = "%s/%s" % (item_uri, name)
            record = {
              "name": data_type["name"],
              "uri": data_type_uri
            }
            nodes["BC_DATA_TYPE"].append(record)
            relationships["HAS_DATA_TYPE"].append({"from": item_uri, "to": data_type_uri})
            if "value_set" in data_type:
              #print(data_type["value_set"])
              for term in data_type["value_set"]: 
                #print(term)
                cl = term["cl"]
                cli = term["cli"]
                term_uri = "%s/%s-%s" % (data_type_uri, cl.lower(), cli.lower())
                record = {
                  "cl": cl,
                  "cli": cli,
                  "uri": term_uri
                }
                nodes["BC_VALUE_SET"].append(record)
                relationships["HAS_RESPONSE"].append({"from": data_type_uri, "to": term_uri})

        # Now all the items
        for item in instance["has_items"]: 
          if item["enabled"]:
            continue
          name = format_name(item["name"])
          collect = False
          if "collect" in item:
            collect = item["collect"]
          item_uri = "%s/%s" % (base_uri, name)
          record = {
            "name": item["name"], 
            "collect": collect,
            "enabled": item["enabled"],
            "uri": item_uri
          }
          nodes["BC_ITEM"].append(record)
          relationships["HAS_ITEM"].append({"from": base_uri, "to": item_uri})
          if qualifier_item == item["name"]:
            relationships["HAS_QUALIFIER"].append({"from": identifier_uri, "to": item_uri})
          if "data_type" in item:
            for data_type in item["data_type"]: 
              name = format_name(data_type["name"])
              data_type_uri = "%s/%s" % (item_uri, name)
              record = {
                "name": data_type["name"],
                "uri": data_type_uri
              }
              nodes["BC_DATA_TYPE"].append(record)
              relationships["HAS_DATA_TYPE"].append({"from": item_uri, "to": data_type_uri})
              if "value_set" in data_type:
                #print(data_type["value_set"])
                for term in data_type["value_set"]: 
                  #print(term)
                  cl = term["cl"]
                  cli = term["cli"]
                  term_uri = "%s/%s-%s" % (data_type_uri, cl.lower(), cli.lower())
                  record = {
                    "cl": cl,
                    "cli": cli,
                    "uri": term_uri
                  }
                  nodes["BC_VALUE_SET"].append(record)
                  relationships["HAS_RESPONSE"].append({"from": data_type_uri, "to": term_uri})

    for k, v in narrower.items():
      if len(v) > 0:
        from_uri = k
        for bc in v:
          to_uri = bc_uri[bc]
          print("Narrower from %s to %s" % (from_uri, to_uri))
          relationships["BC_NARROWER"].append({"from": from_uri, "to": to_uri})

                
delete_dir("load_data/instances")
process()

for k, v in nodes.items():
  csv_filename = "load_data/instances/node-%s-1.csv" % (k.lower())
  write_nodes(v, csv_filename)

for k, v in relationships.items():
  csv_filename = "load_data/instances/relationship-%s-1.csv" % (k.lower())
  write_relationships(v, csv_filename)
