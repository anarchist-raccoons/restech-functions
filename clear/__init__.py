import threading
import logging
from panopta import webhook

def main(req: webhook.REQUEST) -> webhook.RESPONSE:
    '''
    thread = threading.Thread(target=webhook.run, args=("clear", req,))
    logging.info("\nStarting the main clear thread.\n")
    thread.start()
    '''
    webhook.run("clear", req)
    return webhook_response() 



def webhook_response()->webhook.RESPONSE:
    response = webhook.RESPONSE(
            "\nPanopta clear webhook request was received successfully!\n\n",
            status_code=200)
    return response

