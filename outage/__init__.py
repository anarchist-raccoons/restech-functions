import logging
# pip install requests
import requests
import os
import json
from requests.auth import HTTPBasicAuth
from . import cw_connector
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
        ticket_exists = cw_connector.find_ticket(params['outage_id'])
        # check whether ticket exists
        if ticket_exists:
            return { 
                "message": f"Ticket exists {ticket_exists[0]['id']}",
                "status": 200
            }
        else:
            return cw_connector.create_ticket(params)

    else:
        return { 
            "message": "Missing one or more required parameters",
            "status": 422
        }


