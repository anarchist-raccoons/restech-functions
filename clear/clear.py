import logging
from typing import List, Dict 
from azure.functions import HttpRequest as REQUEST
from azure.functions import HttpResponse as RESPONSE

import connectwise.connect as cw


def run(req: REQUEST) -> RESPONSE:
    logging.info('Python HTTP trigger function processed a clear request.')
    return allow_request(req) if req.method == "PATCH" else block_request()


def allow_request(req: REQUEST)->RESPONSE:
    outage = get_clear(req)
    return RESPONSE(outage['message'], status_code=outage['status'])


def block_request(req: REQUEST)->RESPONSE:
    message = f"{req.method} Method Not Allowed"
    return RESPONSE(message,status_code=405)


def get_clear(req: REQUEST) -> Dict:
    logging.info('Clear Received') 
    params = req.get_json()
    logging.info(f"Received: {params}")
    # check if any of the required params is missing
    if not all(param in params for param in panopta_required_params()):
        return missing_param_response()
    ticket_exists = cw.find_ticket(params['outage_id'])
    return cw.close_ticket(params) if ticket_exists else non_existing_ticket()


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
            'cleartime',
            'duration'
            ]



def existing_ticket(ticket: Dict)->Dict:
    return { 
        "message": f"Ticket exists {ticket[0]['id']}",
        "status": 200
        }


def non_existing_ticket()->Dict:
    return { 
        "message": f"Ticket does not exists!",
        "status": 500
        }

def missing_param_response()->Dict:
    return { 
        "message": "Missing one or more required parameters",
        "status": 422
        }

