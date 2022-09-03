import csv
import os
from os import walk
import pathlib

uri_to_id = {}
id_number = 1

def delete_dir(dir_path):
  target_dir = "load_data"
  files = os.listdir(target_dir)
  for f in files:
    os.remove("%s/%s" % (target_dir, f))
    print("Deleted %s" % (f))

def files_in_dir(target_path):
  result = []
  for (dir_path, dir_names, filenames) in walk(target_path):
    for filename in filenames:
  
# function to return the file extension
      if pathlib.Path(filename).suffix == ".yaml":
        result.append("%s/%s" % (dir_path, filename))
  print(result)
  return result

def write_nodes(the_data, csv_filename, id_field="id:ID"):

  global uri_to_id
  global id_number

  if len(the_data) == 0:
    return 
  with open(csv_filename, mode='w', newline='') as csv_file:
    fields = list(the_data[0].keys())
    fieldnames = [id_field] + fields
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writeheader()
    for row in the_data:
      row[id_field] = id_number
      uri_to_id[row["uri"]] = id_number
      id_number += 1
      writer.writerow(row)

def write_relationships(the_data, csv_filename, id_field="id:ID"):

  global uuid_to_id

  if len(the_data) == 0:
    return 
  global id_number
  with open(csv_filename, mode='w', newline='') as csv_file:
    fieldnames = [ ":START_ID", ":END_ID" ]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writeheader()
    for row in the_data:
      new_row = { ":START_ID": uri_to_id[row["from"]], ":END_ID": uri_to_id[row["to"]] }
      writer.writerow(new_row)
