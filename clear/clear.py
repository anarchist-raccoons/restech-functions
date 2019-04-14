import logging
from typing import List, Dict 
from azure.functions import HttpRequest as REQUEST
from azure.functions import HttpResponse as RESPONSE

import connectwise.connect as cw


def run(req: REQUEST) -> RESPONSE:
    logging.info('Python HTTP trigger function processed a clear request.')
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
