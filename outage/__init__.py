import threading
from . import outage

def main(req: outage.REQUEST) -> outage.RESPONSE:
    thread = threading.Thread(target=outage.run, args=(req,))
    logging.info("\nStarting the main outage thread.\n")
    thread.start()
    return webhook_response() 



def webhook_response()->outage.RESPONSE:
    response = outage.RESPONSE(
            "\nPanopta outage webhook request was received successfully!\n",
            status_code=200)
    return response

