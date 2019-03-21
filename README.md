# Introduction 
Azure Functions Serverless Web Service for integration between Panopta and ConnectWise

# Notes

{"customFieldConditions":"caption=\"Outage ID\" AND value=\"THEID\""}

https://azure.microsoft.com/en-gb/blog/benefits-of-using-azure-api-management-with-microservices/

# Variables

customer_id
outage_id
(other bits)

# Components

Azure Functions
Azure Function App
Azure API Management

# Commands

Requires Python 3.6 and virtualenv

virtualenv -p python3.6 DEST

# Functions

# Outage

get customer_id from CW (poss stored as env var)
get service board (poss stored as env var)
create ticket

# Clear

get ticket with outage_id
resolve
add duration etc.
