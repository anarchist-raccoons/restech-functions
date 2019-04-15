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
        body = get_ticket_creation_body(params) 
        data = json.dumps(body)
        r = requests.post( 
                f"{cw_uri()}/service/tickets", 
                headers=__HEADERS,
                data=data,
                auth=(cw_user(), cw_key()))
        return {"message": str(r.json()),
                "status": r.status_code
                } 
    except Exception as e:
        return request_failed("resolution", e)


def resolve_ticket(params)->Dict:
    logging.info('Resolve Ticket')
    try:
        body = get_ticket_resolution_body(params) 
        data = json.dumps(body)
        ticket_id = find_ticket(params['outage_id'])[0]['id']
        logging.info(f"\nTicket ID is {ticket_id}\n")
        r = requests.patch( 
                f"{cw_uri()}/service/tickets/{ticket_id}", 
                headers=__HEADERS,
                data=data,
                auth=(cw_user(), cw_key()))
        update_resolution_note(params)
        return {"message": str(r.json()), "status": r.status_code} 
    except Exception as e:
        return request_failed("resolution", e)


def update_resolution_note(params)->Dict:
    logging.info('updating resolution note')
    try:
        body = get_resolution_note_body(params) 
        data = json.dumps(body)
        ticket_id = find_ticket(params['outage_id'])[0]['id']
        logging.info(f"\nTicket ID is {ticket_id}\n")
        r = requests.post( 
                f"{cw_uri()}/service/tickets/{ticket_id}/notes", 
                headers=__HEADERS,
                data=data,
                auth=(cw_user(), cw_key()))
        return {"message": str(r.json()), "status": r.status_code} 
    except Exception as e:
        return request_failed("updating the notes of the ", e)


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


def cw_resolved():
    return os.getenv('CW_RESOLVED')


def get_company_name_URI(custid: str)->str:
    path = '/company/companies?conditions=identifier="' + custid + '"'
    return f"{cw_uri()}{path}"


def get_ticket_URI(outage_id: str)->str:
    path = f"/service/tickets?customFieldConditions=caption=\"Outage ID\" AND value = {outage_id}"
    return f"{cw_uri()}{path}"


def get_ticket_creation_body(params:Dict)->Dict:
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
    return body


def get_ticket_resolution_body(params:Dict)->List[Dict]:
    status = {"id": cw_resolved()}
    summary = f"Panopta Alert on {params['fqdn']} [{format_duration(params['duration'])}]"
    return [{"op": "replace","path": "status","value": status},
            {"op": "replace","path": "summary","value": summary }]


def get_resolution_note_body(params:Dict)->List[Dict]:
    body = {
            "text": (f"Cleared at: {params['cleartime']}\n"
                f"Duration: {format_duration(params['duration'])}\n"
                f"Duration(s): {params['duration']}"),
            "resolutionFlag": "True"
            }
    return body


def request_failed(action_description:str, exception:Exception)->Dict:
    logging.error(f"Ticket {action_description} Failed:\n{exception}\n")
    return {"message": f"Ticket {action_description} Failed:\n{exception}\n",
            "status": 500}


def convert_duration(seconds:str)->Dict[str,int]:
    seconds = int(seconds)
    __SECS_PER_HOUR = 3600
    __SECS_PER_MIN = 60
    hours = seconds // __SECS_PER_HOUR
    leftover = seconds % __SECS_PER_HOUR
    mins = (leftover // __SECS_PER_MIN) if hours else (seconds // __SECS_PER_MIN)
    return {"hours":hours, "minutes": mins}


def format_duration(duration:int)->str:
    converted_duration = convert_duration(duration)
    duration_str = ""
    if converted_duration["hours"]:
        hour_str = ("hours", "hour")[converted_duration["hours"] == 1]
        duration_str += f"{converted_duration['hours']} {hour_str}" 
    if converted_duration["minutes"]:
        min_str = ("minutes", "minute")[converted_duration["minutes"] == 1]
        duration_str += f" {converted_duration['minutes']} {min_str}" 
    return duration_str.strip()
