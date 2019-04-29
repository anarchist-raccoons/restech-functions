import threading
import logging
from . import clear

def main(req: clear.REQUEST) -> clear.RESPONSE:
    thread = threading.Thread(target=clear.run, args=(req,))
    logging.info("\nStarting the main clear thread.\n")
    thread.start()
    return webhook_response() 



def webhook_response()->clear.RESPONSE:
    response = clear.RESPONSE(
            "\nPanopta clear webhook request was received successfully!\n\n",
            status_code=200)
    return response

