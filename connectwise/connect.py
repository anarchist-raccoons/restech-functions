import logging
from typing import * 
import requests
import os
import json


__APP_JSON =  'application/json'
__HEADERS = {'content-type': __APP_JSON, 'accept': __APP_JSON} 


'''
This module takes care of the data exchange between the application and CW.
'''
def company_name(custid:str)->str:
    logging.info('Get Company ID')
    uri = get_company_name_URI(custid) 
    err_message = "Company request failed" 
    resp = generic_get_request(uri, err_message)
    return resp[0]['id']


def find_ticket(outage_id:str)->Dict:
    logging.info('Find Ticket')
    uri = get_ticket_URI(outage_id) 
    err_message = "Company request failed" 
    return generic_get_request(uri, err_message)


def generic_get_request(uri:str, error_message:str)->Dict:
    try:
        r = requests.get( 
                uri, 
                headers=__HEADERS, 
                auth=(cw_user(), cw_key()))
        return r.json()
    except Exception as e:
        logging.error(error_message + str(e))


def create_ticket(params)->Dict:
    logging.info('Create Ticket')
    try:
        desc = (f"Item(s): {params['items']} \n"
                f"Services: {params['services']}\n"
                f"Reasons: {params['reason']}\n"
                f"Began at: {params['starttime']}")
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
        r = requests.post( 
                f"{cw_uri()}/service/tickets", 
                headers=__HEADERS,
                data=data,
                auth=(cw_user(), cw_key()))
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


def get_company_name_URI(custid: str)->str:
    path = '/company/companies?conditions=identifier="' + custid + '"'
    return f"{cw_uri()}{path}"


def get_ticket_URI(outage_id: str)->str:
    path = f"/service/tickets?customFieldConditions=caption=\"Outage ID\" AND value = {outage_id}"
    return f"{cw_uri()}{path}"
