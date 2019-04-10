import logging
# pip install requests
import requests
import os
import json
#from requests.auth import HTTPBasicAuth

'''
This module takes care of the data exchange between the application and CW.
'''
def company_name(custid):
    logging.info('Get Company ID')
    path = '/company/companies?conditions=identifier="' + custid + '"'
    try:
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        r = requests.get( str(cw_uri()) + str(path) , headers=headers, auth=(cw_user(), cw_key()) )
        return r.json()[0]['id']
    except Exception as e:
        logging.error(f"Company request failed {e}")
        return int(os.getenv('CW_CATCHALL'))

def find_ticket(outage_id):
    logging.info('Find Ticket')
    try:
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        r = requests.get( f"{cw_uri()}/service/tickets?customFieldConditions=caption=\"Outage ID\" AND value = {outage_id}" , headers=headers, auth=(cw_user(), cw_key()) )
        return r.json()
    except Exception as e:
        logging.error(f"Ticket find Failed {e}")
        return
    
def create_ticket(params):
    logging.info('Create Ticket')
    try:
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        desc = f"Item(s): {params['items']} \nServices: {params['services']} \nReasons: {params['reason']}\nBegan at: {params['starttime']}"
        body = { 
         "summary": f"Panopta Alert on {params['fqdn']}" ,
         "company": { "id": int(company_name(params['Company_name'])) }, 
         "recordType": "ServiceTicket", 
         "board": { "id": int(service_board()) },
         "initialDescription": desc,
         "customFields": [
             {
                'id': 60, 
                'caption': 'Outage ID', 
                'type': 'Text', 
                'entryMethod': 'EntryField', 
                'numberOfDecimals': 0,
                'value': params['outage_id']
             }
            ]
        }
        data = json.dumps(body)
        r = requests.post( f"{cw_uri()}/service/tickets" , headers=headers, data=data, auth=(cw_user(), cw_key()) )
        return { 
            "message": str(r.json()),
            "status": r.status_code
        } 
    except Exception as e:
        logging.error(f"Ticket creation Failed {e}")
        return { 
            "message": f"Ticket creation Failed {e}",
            "status": 500
        }
        
def service_board():
    return os.getenv('CW_SERVICE_BOARD')

def cw_key():
    return os.getenv('CW_KEY')

def cw_user():
    return os.getenv('CW_USER')
    
def cw_uri():
    return os.getenv('CW_URI')
    
def cw_catchall():
    return os.getenv('CW_CATCHALL')

