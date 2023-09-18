
# Your Twilio account SID and auth token
from twilio.rest import Client
account_sid = "AC128cd917b12c6f6000b2cab8ec288d7a"
auth_token = "c7689cc59ed587fff88ab1352254d36f"

# Initialize the Twilio client
client = Client(account_sid, auth_token)

# Retrieve the list of purchased phone numbers
numbers = client.incoming_phone_numbers.list()

# Print the phone numbers
for number in numbers:
    print(number.phone_number)
