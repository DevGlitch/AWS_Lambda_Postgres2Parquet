import json
from lambda_function import lambda_handler


with open("test_event.json", "r") as event_file:
    event = json.load(event_file)

context = None  # You can create a mock context object if needed

response = lambda_handler(event, context)
print(response)
