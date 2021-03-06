import logging
from typing import List, Dict 
from azure.functions import HttpRequest as REQUEST
from azure.functions import HttpResponse as RESPONSE

import connectwise.connect as cw


def run(func_type:str, req: REQUEST) -> RESPONSE:
    logging.basicConfig(level=logging.INFO)
    logging.info('\nPython HTTP trigger function processed a clear request.\n')
    return allow_request(func_type, req) if req.method == "POST" else block_request(req)


def allow_request(func_type:str, req: REQUEST)->RESPONSE:
    function = globals()[func_type](req) 
    return RESPONSE(function['message'], status_code=function['status'])


def block_request(req: REQUEST)->RESPONSE:
    message = f"{req.method} Method Not Allowed\n"
    return RESPONSE(message,status_code=405)


def clear(req: REQUEST) -> Dict:
    logging.info('\nClear Received\n') 
    params = req.get_json()
    logging.info(f"\nReceived: {params}\n")
    # check if any of the required params is missing
    if not all(param in params for param in panopta_required_params()):
        return missing_param_response()
    ticket_exists = cw.find_ticket(params['outage_id'])
    if ticket_exists:
        return cw.resolve_ticket(params) 
    else:
        return cw.create_and_resolve(params)


def outage(req: REQUEST) -> Dict:
    logging.info('Outage Received') 
    params = req.get_json()
    logging.info(f"Received: {params}")
    # check if any of the required params is missing
    if not all(param in params for param in panopta_required_params()):
        return missing_param_response()
    ticket_exists = cw.find_ticket(params['outage_id'])
    if ticket_exists:
        return existing_ticket(ticket_exists) 
    else:
        return cw.create_ticket(params)



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
            'starttime',
            'duration'
            ]


def existing_ticket(ticket: Dict)->Dict:
    return { 
        "message": f"Ticket exists {ticket[0]['id']}",
        "status": 200
        }


def non_existing_ticket()->Dict:
    return { 
        "message": f"\nTicket does not exists!\n",
        "status": 500
        }

def missing_param_response()->Dict:
    return { 
        "message": "\nMissing one or more required parameters!\nCheck the paramaters list in the Panopta Webhook menu.\n",
        "status": 422
        }
