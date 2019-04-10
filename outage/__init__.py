from . import outage

def main(req: outage.REQUEST) -> outage.RESPONSE:
    return outage.run(req)
