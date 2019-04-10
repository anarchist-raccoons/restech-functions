import logging
from typing import List, Dict 
from azure.functions import HttpRequest as REQUEST
from azure.functions import HttpResponse as RESPONSE

import connectwise.connect as cw

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

def run(req: REQUEST) -> RESPONSE:
    logging.info('Python HTTP trigger function processed an outage request.')
    return allow_request(req) if req.method == "POST" else block_request()



def allow_request(req: REQUEST)->RESPONSE:
    outage = get_outage(req)
    return RESPONSE(outage['message'], status_code=outage['status'])



def block_request(req: REQUEST)->RESPONSE:
    message = f"{req.method} Method Not Allowed"
    return RESPONSE(message,status_code=405)



def get_outage(req: REQUEST) -> Dict:
    logging.info('Outage Received') 
    params = req.get_json()
    logging.info(f"Received: {params}")
    # check if any of the required params is missing
    if not all(param in params for param in panopta_required_params()):
        return missing_param_response()
    ticket_exists = cw.find_ticket(params['outage_id'])
    return existing_ticket(ticket_exists) if ticket_exists else cw.create_ticket(params)



'''
Returns a list of the params required by Panopta
'''
def panopta_required_params()->List[str]:
    return ['Company_name', 
            'outage_id',
            'fqdn',
            'reason',
            'services',
            'items',
            'starttime'
            ]



def existing_ticket(ticket: Dict)->Dict:
    return { 
        "message": f"Ticket exists {ticket[0]['id']}",
        "status": 200
        }



def missing_param_response()->Dict:
    return { 
        "message": "Missing one or more required parameters",
        "status": 422
        }

