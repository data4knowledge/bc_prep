
from utility.utility import *

DATA_TYPES = {
  "date_time": {
    "parent": {
      "name": "date_time",
    },
    "child": {
      "value": { 
        "name": "value" ,
      }
    }
  },
  "string": {
    "parent": {
      "name": "string",
    },
    "child": {
      "value": { 
        "name": "text" ,
      }
    }
  },
  "quantity": {
    "parent": {
      "name": "quantity",
    },
    "child": {
      "value": { 
        "name": "value",
      },
      "code": { 
        "name": "code",
      },
      "unit": { 
        "name": "unit" ,
      },
      "system": { 
        "name": "system" ,
      },
      "comparator": { 
        "name": "comparator" ,
      }
    }
  },
  "codeable_concept": {
    "parent": {
      "name": "codeable concept" ,
    },
    "child": {
      "text": { 
        "name": "text" ,
      },
      "coding": { 
        "recurse": True,
      },
    }
  },
  "coding": { 
    "parent": {
      "name": "coding",
    },
    "child": {
      "code": { 
        "name": "code",
      },
      "userSelected": { 
        "name": "user selected",
      },
      "version": { 
        "name": "version",
      },
      "system": { 
        "name": "system",
      },
      "display": { 
        "name": "display",
      }    
    }      
  }
}	

def add_data_type(parent_name, parent_uri, data_type, nodes, relationships, crm_paths, crm_map, path = ""):
  dt = DATA_TYPES[data_type]
  name = format_name(dt['parent']['name'])
  item_uri = "%s/%s" % (parent_uri, name)
  record = {
    "name": name,
    "uri": item_uri
  }
  crm_path = name
  nodes["DataType"].append(record)
  for k, v in dt["child"].items():
    if 'recurse' in v:
      child_uri = add_data_type(parent_name, item_uri, k, nodes, relationships, crm_paths, crm_path)
    else:
      name = v['name']
      child_uri = "%s/%s" % (item_uri, format_name(name))
      path = "%s.%s" % (crm_path, name)
      #print("NAME:", parent_name)
      if parent_name in crm_map:
        #print("CRM MAP:", crm_map[parent_name])
        #print("CRM PATH:", crm_paths[crm_map[parent_name]])
        #print("PATH:", path)
        #print("CRM PATH:", crm_paths[crm_map[parent_name]]["%s.%s" % (crm_map[parent_name], path)])
        crm_uri = crm_paths[crm_map[parent_name]]["%s.%s" % (crm_map[parent_name], path)]
      else:
        crm_uri = None
      record = {
        "name": name,
        "uri": child_uri,
        "crm_uri": crm_uri,
        "uuid": uuid4()
      }
      nodes["DataTypeProperty"].append(record)
      #print(record)
    relationships["HAS_PROPERTY"].append({"from": item_uri, "to": child_uri})
  return item_uri
    
