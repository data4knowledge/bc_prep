import yaml
from utility.utility import *

dict = {
  "Base Laboratory":
    {
      "--POS": "Position",
      "--LOC": "Site of Administration",
      "--LAT": "Laterality",
      "--METHOD": "Method",
      "--ORRES": "Result",
      "--DIR": "Directionality",
      "--SPEC": "Specimen"
    },
    "Base Observation":
      {
      "--POS": "Position",
      "--LOC": "Site of Administration",
      "--LAT": "Laterality",
      "--METHOD": "Method",
      "--ORRES": "Result",
      "--SPEC": "Specimen"
      }
} 

def process_instances():
  files = files_in_dir('source_data/cdisc')
  for filename in files:
    with open(filename, "r+") as file:
      instance = yaml.load(file, Loader=yaml.FullLoader)
      bc_file_name = instance['datasetSpecializationId']
      bc = []
      bc = {
        'name': instance['shortName'],
        'identifier': instance['datasetSpecializationId'],
        'based_on':'',
        'identified_by':
        {
          'name':'Test',
          'enabled': True, 
          'collect': False,
          'data_type': []
        },
        'has_items': []
      } 
      
      x = {'name':'coding',
           'value_set': 
           [
             {
              'cl': "TO BE LOOKED UP",
              'cli': instance['biomedicalConceptId'] 
             }
           ]
          }
      bc['identified_by']['data_type'].append(x)
      if filename.__contains__('_lb_'):
         bc['based_on'] = 'Base Laboratory'
      else:
          bc['based_on'] = 'Base Observation'   
      
      bc['has_items'] = []
      for var in instance['variables']:        
        #replace the e.g. VSPOS to --POS
        var['name'] =  '--' +  var['name'][2:]
        if  var['name'] not in(['--TEST','--TESTCD','--ORRESU','--STRESC','--STRESN','--STRESU','--CAT','--LOINC','--FAST']) : 
          if 'dataType' in var:
           record = {
            'name': dict[bc['based_on']][var['name']],
            'enabled':True,
            'data_type': 
            [
              {'name':'quantity',
               'value_set': []
              }
            ]
          }
          else:
            record = {
            'name': dict[bc['based_on']][var['name']],
            'enabled':True,
            'data_type':
            [
              {
                'name':'coding',
                'value_set': []
              }
            ]
          }
            bc['has_items'].append(record)
            
          if 'valueList' in var:
            for value in var['valueList']:
              rec = {
                      'cl':"TO BE LOOKED UP",
                      "cli": value
                    }
              record['data_type'][0]['value_set'].append(rec)
            
    if filename.find('_lb_'):
      path = 'converted_data/'
      filename = path+bc_file_name+'.yaml'
      with open(filename, 'w') as file:
        yaml.dump([bc], file,sort_keys=False)

process_instances()                
