from azure.functions import HttpRequest as request
from azure.functions import HttpResponse as response
from . import outage

def main(req: request) -> response:
    return outage.run(req)
