import pywhatkit

# Replace with the actual phone number and message
phone_number = "+96893312620"  # Include country code
message = "This is an automated message sent via Python!"

# Schedule the message to be sent at 10:30 AM
# (Adjust hour and minute as needed)
hour = 10
minute = 30

try:
    pywhatkit.sendwhatmsg(phone_number, message, hour, minute)
    print(f"WhatsApp message scheduled to {phone_number} at {hour:02d}:{minute:02d}.")
except Exception as e:
    print(f"An error occurred: {e}")