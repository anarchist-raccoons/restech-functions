#import threading
import logging
from panopta import webhook

def main(req: webhook.REQUEST) -> webhook.RESPONSE:
    webhook.run("clear", req)
    return webhook_response() 


def webhook_response()->webhook.RESPONSE:
    response = webhook.RESPONSE(
            "\nPanopta clear webhook request was received successfully!\n\n",
            status_code=200)
    return response

