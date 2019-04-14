from . import clear

def main(req: clear.REQUEST) -> clear.RESPONSE:
    return clear.run(req)
