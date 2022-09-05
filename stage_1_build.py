import yaml
from utility.utility import *
from utility.ra_server import *
from utility.crm_server import *
from stringcase import pascalcase, snakecase
from utility.fhir import add_data_type
nodes = { 
  "Template": [], "Instance": [], "TemplateItem": [], "InstanceItem": [], "DataType": [], "DataTypeProperty": [], "ValueSet": [],
  'ScopedIdentifier': [], 'Namespace': [], 'RegistrationStatus': [], 'RegistrationAuthority': [] 
}
relationships = { 
  "BASED_ON": [], "HAS_ITEM": [], "HAS_IDENTIFIER": [], "HAS_QUALIFIER": [], "BC_NARROWER": [], "HAS_DATA_TYPE": [], "HAS_PROPERTY": [], "HAS_RESPONSE": [],
  "IDENTIFIED_BY": [], "HAS_STATUS": [], "SCOPED_BY": [], "MANAGED_BY": [],
}
bc_uri = {}
#uri_to_id = {}

def process_templates(the_instance_uri, ns_uri, ra_uri):
  with open("source_data/templates/templates.yaml") as file:
    templates = yaml.load(file, Loader=yaml.FullLoader)
    for template in templates:
      the_template_uri = template_uri(the_instance_uri, template["name"])
      #print("Template:", template["name"], the_template_uri)
      nodes["Template"].append({"name": template["name"], "uri": the_template_uri})
      add_identifier_and_status(the_template_uri, template["name"].upper(), "2022-09-01", ns_uri, ra_uri, nodes, relationships)
      name = format_name(template["identified_by"]["name"])
      item_uri = "%s/%s" % (the_template_uri, name)
      record = {
        "name": template["identified_by"]["name"], 
        "mandatory": template["identified_by"]["mandatory"],
        "enabled": template["identified_by"]["enabled"],
        "uri": item_uri,
        "canonical": ""
      }
      if "canonical" in template["identified_by"]:
        record["canonical"] = template["identified_by"]["canonical"]
        crm_server = CRMServer()
        result = crm_server.crm_node_data_types(template["identified_by"]["canonical"])
        print("CRM:", record["canonical"], result)
      nodes["TemplateItem"].append(record)
      relationships["HAS_ITEM"].append({"from": the_template_uri, "to": item_uri})
      relationships["HAS_IDENTIFIER"].append({"from": the_template_uri, "to": item_uri})

      parent_uri = item_uri
      name = format_name(template["identified_by"]["data_type"][0]["name"])
      item_uri = "%s/%s" % (parent_uri, name)
      record = {
        "name": template["identified_by"]["data_type"][0]["name"],
        "uri": item_uri
      }
      nodes["DataType"].append(record)
      relationships["HAS_DATA_TYPE"].append({"from": parent_uri, "to": item_uri})

      # Now all the items
      for item in template["has_items"]: 
        name = format_name(item["name"])
        item_uri = "%s/%s" % (the_instance_uri, name)
        record = {
          "name": item["name"], 
          "mandatory": item["mandatory"],
          "enabled": item["enabled"],
          "uri": item_uri,
          "canonical": ""
        }
        if "canonical" in item:
          record["canonical"] = item["canonical"]
          crm_server = CRMServer()
          result = crm_server.crm_node_data_types(item["canonical"])
          print("CRM:", record["canonical"], result)
        nodes["TemplateItem"].append(record)
        relationships["HAS_ITEM"].append({"from": the_template_uri, "to": item_uri})
        parent_uri = item_uri
        for data_type in item["data_type"]: 
          name = format_name(data_type["name"])
          item_uri = "%s/%s" % (parent_uri, name)
          record = {
            "name": data_type["name"],
            "uri": item_uri
          }
          nodes["DataType"].append(record)
          relationships["HAS_DATA_TYPE"].append({"from": parent_uri, "to": item_uri})

def process_instances(base_uri, ns_uri, ra_uri):
  files = files_in_dir('source_data/instances')
  for filename in files:
    with open(filename) as file:
      narrower = {}
      instances = yaml.load(file, Loader=yaml.FullLoader)
      for instance in instances:
        #print(instance)
        #print("instance:", instance["name"])
        based_on_uri = template_uri(base_uri, instance["based_on"])
        #print("based on:", based_on_uri)
        the_instance_uri, uri_name = instance_uri(base_uri, instance["name"])
        nodes["Instance"].append({"name": instance["name"], "uri": the_instance_uri})           
        relationships["BASED_ON"].append({"from": the_instance_uri, "to": based_on_uri})
        add_identifier_and_status(the_instance_uri, instance["name"].upper(), "2022-09-01", ns_uri, ra_uri, nodes, relationships)
        bc_uri[uri_name] = the_instance_uri
        narrower[the_instance_uri] = []
        if "narrower" in instance:
          for children in instance["narrower"]:
            narrower[the_instance_uri].append(format_name(children))
        # Identifier Node and Associated Data Type
        item = instance["identified_by"]
        qualifier_item = ""
        if "qualified_by" in item:
          qualifier_item = item["qualified_by"]
        name = format_name(item["name"])
        item_uri = "%s/%s" % (the_instance_uri, name)
        identifier_uri = item_uri
        collect = False
        if "collect" in item:
          collect = item["collect"]
        record = {
          "name": item["name"], 
          "collect": collect,
          "enabled": item["enabled"],
          "uri": item_uri
        }
        nodes["InstanceItem"].append(record)
        relationships["HAS_ITEM"].append({"from": the_instance_uri, "to": item_uri})
        relationships["HAS_IDENTIFIER"].append({"from": the_instance_uri, "to": item_uri})
        if "data_type" in item:
          for data_type in item["data_type"]: 
            dt_uri = add_data_type(item_uri, data_type["name"], nodes, relationships)
            relationships["HAS_DATA_TYPE"].append({"from": item_uri, "to": dt_uri})
            if "value_set" in data_type:
              #print(data_type["value_set"])
              for term in data_type["value_set"]: 
                #print(term)
                cl = term["cl"]
                cli = term["cli"]
                term_uri = "%s/%s-%s" % (dt_uri, cl.lower(), cli.lower())
                record = {
                  "cl": cl,
                  "cli": cli,
                  "uri": term_uri
                }
                nodes["ValueSet"].append(record)
                relationships["HAS_RESPONSE"].append({"from": dt_uri, "to": term_uri})

        # Now all the items
        for item in instance["has_items"]: 
          #print("Enabled:", item["enabled"])
          if not item["enabled"]:
            continue
          name = format_name(item["name"])
          collect = False
          if "collect" in item:
            collect = item["collect"]
          item_uri = "%s/%s" % (the_instance_uri, name)
          record = {
            "name": item["name"], 
            "collect": collect,
            "enabled": item["enabled"],
            "uri": item_uri
          }
          nodes["InstanceItem"].append(record)
          relationships["HAS_ITEM"].append({"from": the_instance_uri, "to": item_uri})
          #print("Rel: [from: %s, to: %s]" % (the_instance_uri, item_uri))
          if qualifier_item == item["name"]:
            relationships["HAS_QUALIFIER"].append({"from": identifier_uri, "to": item_uri})
          if "data_type" in item:
            for data_type in item["data_type"]: 
              dt_uri = add_data_type(item_uri, data_type["name"], nodes, relationships)
              relationships["HAS_DATA_TYPE"].append({"from": item_uri, "to": dt_uri})
              if "value_set" in data_type:
                #print(data_type["value_set"])
                for term in data_type["value_set"]: 
                  #print(term)
                  cl = term["cl"]
                  cli = term["cli"]
                  term_uri = "%s/%s-%s" % (dt_uri, cl.lower(), cli.lower())
                  record = {
                    "cl": cl,
                    "cli": cli,
                    "uri": term_uri
                  }
                  nodes["ValueSet"].append(record)
                  relationships["HAS_RESPONSE"].append({"from": dt_uri, "to": term_uri})

    for k, v in narrower.items():
      if len(v) > 0:
        from_uri = k
        for bc in v:
          to_uri = bc_uri[bc]
          #print("Narrower from %s to %s" % (from_uri, to_uri))
          relationships["BC_NARROWER"].append({"from": from_uri, "to": to_uri})

delete_dir("load_data")

ns_s_json = RaServer().namespace_by_name("d4k BC namespace")
#print(ns_s_json)
ra_s_json = RaServer().registration_authority_by_namespace_uuid(ns_s_json['uuid'])
#print(ra_s_json)

process_templates(ns_s_json['value'], ns_s_json['uri'], ra_s_json['uri'])
process_instances(ns_s_json['value'], ns_s_json['uri'], ra_s_json['uri'])

for k, v in nodes.items():
  csv_filename = "load_data/node-%s-1.csv" % (snakecase(k))
  write_nodes(v, csv_filename)

for k, v in relationships.items():
  csv_filename = "load_data/relationship-%s-1.csv" % (k.lower())
  write_relationships(v, csv_filename)
