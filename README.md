# Introduction 
Azure Functions Serverless Web Service for integration between Panopta and Connect

# Reference

https://docs.microsoft.com/en-gb/azure/azure-functions/functions-create-first-function-python

# Setup

npm install -g azure-functions-core-tools

Requires Python 3.6 and virtualenv

```
# do this just once
python3.6 -m venv .env
source .env/bin/activate
func init
>> choose option 3. python

# do this each time you need the virtualenv
source .env/bin/activate

# do this for each new function
func new 
>> choose a template
>> provide a name (this creates a directory with the function code)
func start # start locally
func azure functionapp publish FUNCTION_APP_NAME # publish to azure
```

# Variables

* Company_id
* outage_id
* items
* reason
* services
* fqdn
* starttime

# Functions

# Outage

1) check for required variables
2) get customer_id from CW
3) create ticket

# Clear

get ticket with outage_id
resolve
add duration etc.
