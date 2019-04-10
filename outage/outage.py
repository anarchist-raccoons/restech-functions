import logging
# pip install requests
import requests
import os
import json
from requests.auth import HTTPBasicAuth
from typing import List
import azure.functions as func

from . import cw_connector as cw

'''
 Create a ticket in ConnectWise on receipt of Outage Information
   Required ENV VARS:
     CW_SERVICE_BOARD (find with GET https://api-eu.myconnectwise.net/v4_6_release/apis/3.0/service/boards/ )
     CW_USER (setup in Account), enter as cosector+
     CW_KEY (setup in Account)
     CW_URL (eg. https://api-eu.myconnectwise.net/v4_6_release/apis/3.0)

  Set in the Azure App Service > Application Settings

 @todo - secure the endpoint via IP restriction, or match the source URL
'''



def run(req: func.HttpRequest) -> func.HttpResponse:
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
    required_params = get_required_params()
    logging.info(f"Received: {params}")
    # check all params are present
    if len([x for x in required_params if x in params]) == len(required_params):
        ticket_exists = cw.find_ticket(params['outage_id'])
        # check whether ticket exists
        if ticket_exists:
            return { 
                "message": f"Ticket exists {ticket_exists[0]['id']}",
                "status": 200
            }
        else:
            return cw.create_ticket(params)

    else:
        return { 
            "message": "Missing one or more required parameters",
            "status": 422
        }



'''
Returns a list of the params required by Panopta
'''
def get_required_params()->List[str]:
    return ['Company_name', 
            'outage_id',
            'fqdn',
            'reason',
            'services',
            'items',
            'starttime'
            ]
