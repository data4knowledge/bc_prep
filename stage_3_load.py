from neo4j import GraphDatabase
import os
import glob
from stringcase import pascalcase, snakecase

def file_load(driver, subdir):
  project_root = os.path.abspath(os.path.dirname(__file__))
  load_files = []
  for filename in glob.glob("load_data/%s/*.csv" % (subdir)):
    parts = filename.replace("load_data/%s/" % (subdir), "").split("-")
    file_path = os.path.join(project_root, filename)
    #print(file_path)
    if parts[0] == "node":
      load_files.append({ "label": pascalcase(parts[1]), "filename": file_path })
    else:
      load_files.append({ "type": parts[1].upper(), "filename": file_path })

  result = None
  session = driver.session()
  nodes = []
  relationships = []
  for file_item in load_files:
    if "label" in file_item:
      nodes.append("{ fileName: '%s', labels: ['%s'] }" % (file_item["filename"], file_item["label"]) )
    else:
      relationships.append("{ fileName: '%s', type: '%s' }" % (file_item["filename"], file_item["type"]) )
  query = """CALL apoc.import.csv( [%s], [%s], {stringIds: false})""" % (", ".join(nodes), ", ".join(relationships))
  result = session.run(query)
  for record in result:
    return_value = {'nodes': record['nodes'], 'relationships': record['relationships'], 'time': record['time']}
  driver.close()
  return return_value

def clear(tx):
  tx.run("CALL apoc.periodic.iterate('MATCH (n) WHERE NOT n:`_Neodash_Dashboard` RETURN n', 'DETACH DELETE n', {batchSize:1000})")

def clear_neo4j(driver):
  with driver.session() as session:
    session.write_transaction(clear)
  driver.close()

driver = GraphDatabase.driver("bolt://localhost:7687/", auth=("neo4j", "cdisc"))
database = "neo4j"

print("Deleting database ...")
clear_neo4j(driver)
print("Database deleted. Load new data ...")
result = file_load(driver, "templates")
print("Templates load complete. %s nodes and %s relationships loaded in %s milliseconds." % (result['nodes'], result['relationships'], result['time']))
result = file_load(driver, "instances")
print("Instances load complete. %s nodes and %s relationships loaded in %s milliseconds." % (result['nodes'], result['relationships'], result['time']))

