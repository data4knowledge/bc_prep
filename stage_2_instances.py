import yaml
from utility.utility import *

nodes = { "BC_TEMPLATE": [], "BC_INSTANCE": [], "BC_ITEM": [], "BC_DATA_TYPE": [], "BC_VALUE_SET": [] }
relationships = { "BASED_ON": [], "HAS_ITEM": [], "HAS_IDENTIFIER": [], "HAS_QUALIFIER": [], "BC_NARROWER": [], "HAS_DATA_TYPE": [], "HAS_RESPONSE": [] }
bc_uri = {}
uri_to_id = {}

def process_templates():
  with open("source_data/templates/templates.yaml") as file:
    templates = yaml.load(file, Loader=yaml.FullLoader)
    for template in templates:
      print("Template:", template["name"])
      base_uri = template_uri(template["name"])
      nodes["BC_TEMPLATE"].append({"name": template["name"], "uri": base_uri})

      # Identifier Node and Associated Data Type
      name = format_name(template["identified_by"]["name"])
      item_uri = "%s/%s" % (base_uri, name)
      record = {
        "name": template["identified_by"]["name"], 
        "mandatory": template["identified_by"]["mandatory"],
        "enabled": template["identified_by"]["enabled"],
        "uri": item_uri,
        "canonical": ""
      }
      if ":canonical" in template["identified_by"]:
        record["canonical"] = template["identified_by"]["canonical"]
      nodes["BC_ITEM"].append(record)
      relationships["HAS_ITEM"].append({"from": base_uri, "to": item_uri})
      relationships["HAS_IDENTIFIER"].append({"from": base_uri, "to": item_uri})

      parent_uri = item_uri
      name = format_name(template["identified_by"]["data_type"][0]["name"])
      item_uri = "%s/%s" % (parent_uri, name)
      record = {
        "name": template["identified_by"]["data_type"][0]["name"],
        "uri": item_uri
      }
      nodes["BC_DATA_TYPE"].append(record)
      relationships["HAS_DATA_TYPE"].append({"from": parent_uri, "to": item_uri})

      # Now all the items
      for item in template["has_items"]: 
        name = format_name(item["name"])
        item_uri = "%s/%s" % (base_uri, name)
        record = {
          "name": item["name"], 
          "mandatory": item["mandatory"],
          "enabled": item["enabled"],
          "uri": item_uri,
          "canonical": ""
        }
        if ":canonical" in item:
          record["canonical"] = item["canonical"]
        nodes["BC_ITEM"].append(record)
        relationships["HAS_ITEM"].append({"from": base_uri, "to": item_uri})
        parent_uri = item_uri
        for data_type in item["data_type"]: 
          name = format_name(data_type["name"])
          item_uri = "%s/%s" % (parent_uri, name)
          record = {
            "name": data_type["name"],
            "uri": item_uri
          }
          nodes["BC_DATA_TYPE"].append(record)
          relationships["HAS_DATA_TYPE"].append({"from": parent_uri, "to": item_uri})

def process_instances():
  files = files_in_dir('source_data/instances')
  for filename in files:
    with open(filename) as file:
      narrower = {}
      instances = yaml.load(file, Loader=yaml.FullLoader)
      for instance in instances:
        #print(instance)
        print("instance:", instance["name"])
        based_on_uri = template_uri(instance["based_on"])
        base_uri, uri_name = instance_uri(instance["name"])
        nodes["BC_INSTANCE"].append({"name": instance["name"], "uri": base_uri})           
        relationships["BASED_ON"].append({"from": base_uri, "to": based_on_uri})
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
          print("Enabled:", item["enabled"])
          if not item["enabled"]:
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
          print("Rel: [from: %s, to: %s]" % (base_uri, item_uri))
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

                
delete_dir("load_data")
process_templates()
process_instances()

for k, v in nodes.items():
  csv_filename = "load_data/node-%s-1.csv" % (k.lower())
  write_nodes(v, csv_filename)

for k, v in relationships.items():
  csv_filename = "load_data/relationship-%s-1.csv" % (k.lower())
  write_relationships(v, csv_filename)
