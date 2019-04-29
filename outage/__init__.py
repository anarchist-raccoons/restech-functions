import threading
from . import outage

def main(req: outage.REQUEST) -> outage.RESPONSE:
    thread = threading.Thread(target=outage.run, args=(req,))
    thread.start()
    return webhook_response() 



def webhook_response()->outage.RESPONSE:
    response = outage.RESPONSE(
            "Panopta outage webhook request received",
            status_code=200)
    return response

