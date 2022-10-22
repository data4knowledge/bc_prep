import http
import yaml
from utility.utility import *
import requests
from utility.service_environment import ServiceEnvironment

CTService =  'http://localhost:8012/'

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
      bc_file_name = instance.get('datasetSpecializationId')
      bc = []
      bc = {
        'name': instance['shortName'],
        'identifier': instance.get('datasetSpecializationId'),
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
      
      if instance.get('biomedicalConceptId') is not None:
        ct_url = CTService + 'v1/terms?identifier=' + instance['biomedicalConceptId']
        r = requests.get(ct_url)
        cls = r.json()
        if not len(cls):
          print('Codelist for code '+instance['biomedicalConceptId']+' cannot be found')
          x = {'name':'coding',
                'value_set': 
                [
                {
                'cl': 'NA' ,
                'cli': instance['biomedicalConceptId']
                }
                ]
               }
          bc['identified_by']['data_type'].append(x)
        else:   
         for cl in cls :
        #Get the SDTM codelist for the TESTCD
          if instance['biomedicalConceptId'] == 'C164634':
           print('cl is:'+cl)
          if cl['parent']['uri'].__contains__('sdtm') & cl['parent']['uri'].__contains__('2022') & cl['parent']['notation'].__contains__('TESTCD') :
           codeList = cl['parent']['identifier'] 
                     
           x = {'name':'coding',
                'value_set': 
                [
                {
                'cl': codeList ,
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
        if instance.get('variables') is not None:
         for var in instance['variables']:        
        #replace the e.g. VSPOS to --POS
          var['name'] =  '--' +  var['name'][2:]
          if var['name'] not in(['--TEST','--TESTCD','--ORRESU','--STRESC','--STRESN','--STRESU','--CAT','--LOINC','--FAST']) : 
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
              if value.__contains__('NEW'):
               rec = {
                     'cl': 'NA',
                     "cli": value
                   }
               record['data_type'][0]['value_set'].append(rec)
              else:
               cli_url = CTService + 'v1/terms?notation=' + value
               x = requests.get(cli_url)
               cli = x.json()
               for cl in cli :
                if cl['parent']['uri'].__contains__('sdtm') & cl['parent']['uri'].__contains__('2022') :
                 if cl['parent']['notation'] != 'PKUNIT' : 
                  codeList = cl['parent']['identifier']
                  codeListItem = cl['child']['identifier']
                  rec = {
                     'cl': codeList,
                     "cli": codeListItem
                   }
                  record['data_type'][0]['value_set'].append(rec)
            
    #if filename.__contains__('_vs_'):
      path = 'converted_data/'
      if bc_file_name is not None:
       filename = path+bc_file_name+'.yaml'
       with open(filename, 'w') as file:
        yaml.dump([bc], file,sort_keys=False)

process_instances()                
