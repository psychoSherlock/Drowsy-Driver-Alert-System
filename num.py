
# Your Twilio account SID and auth token
from twilio.rest import Client
account_sid = "***********************"
auth_token = "************************"

# Initialize the Twilio client
client = Client(account_sid, auth_token)

# Retrieve the list of purchased phone numbers
numbers = client.incoming_phone_numbers.list()

# Print the phone numbers
for number in numbers:
    print(number.phone_number)
