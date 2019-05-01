import threading
import logging
from panopta import webhook

def main(req: webhook.REQUEST) -> webhook.RESPONSE:
    '''
    thread = threading.Thread(target=webhook.run, args=("outage", req,))
    logging.info("\nStarting the main outage thread.\n")
    thread.start()
    '''
    webhook.run("outage", req)
    return webhook_response() 



def webhook_response()->webhook.RESPONSE:
    response = webhook.RESPONSE(
            "\nPanopta outage webhook request was received successfully!\n\n",
            status_code=200)
    return response

