import logging
# pip install requests
import requests
import os
import json
from requests.auth import HTTPBasicAuth

import azure.functions as func

# Create a ticket in ConnectWise on receipt of Outage Information
#   Required ENV VARS:
#     CW_SERVICE_BOARD (find with GET https://api-eu.myconnectwise.net/v4_6_release/apis/3.0/service/boards/ )
#     CW_USER (setup in Account), enter as cosector+
#     CW_KEY (setup in Account)
#     CW_URL (eg. https://api-eu.myconnectwise.net/v4_6_release/apis/3.0)
#
#  Set in the Azure App Service > Application Settings

# @todo - secure the endpoint via IP restriction, or match the source URL

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed an outage request.')

    if req.method == "POST":
        outage = receive_outage(req)
        return func.HttpResponse(
            outage['message'],status_code=outage['status']
        )
    else:
        return func.HttpResponse(
            f"{req.method} Method Not Allowed",
            status_code=405
        )

def receive_outage(req):
    logging.info('Outage Received')
    params = req.get_json()
    logging.info(f"Received: {params}")
    # check all params are present
    if 'Company_name' in params and 'outage_id' in params and 'fqdn' in params and 'reason' in params and 'services' in params and 'items' in params and 'starttime' in params:
        ticket_exists = find_ticket(params['outage_id'])
        # check whether ticket exists
        if ticket_exists != None:
            return { 
                "message": f"Ticket exists {ticket_exists[0]['id']}",
                "status": 200
            }
        else:
            return create_ticket(params)
    else:
        return { 
            "message": "Missing one or more required parameters",
            "status": 422
        }

def company_name(custid):
    logging.info('Get Company ID')
    path = '/company/companies?conditions=identifier="' + custid + '"'
    try:
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        r = requests.get( cw_uri() + path , headers=headers, auth=(cw_user(), cw_key()) )
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
        None
    
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
         "description": desc,
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