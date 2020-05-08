import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# https://2.python-requests.org/en/master/
import requests

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def add_subscriber(list_id, api_key, email_address, first_name="", last_name="", phone_number=""):
    """
    Add a Mailchimp subscriber to the audience with the given list_id
    using the given api_key and other personal information.
    """
    # This is the URL we want to send our Mailchimp request to:
    url = f"https://us4.api.mailchimp.com/3.0/lists/{list_id}/members"
    # This is the data about our subscriber
    # that we are going to send to Mailchimp:
    data = {
        "email_address": email_address,
        "status": "subscribed",
        "merge_fields": {
            "FNAME": first_name,
            "LNAME": last_name,
            "PHONE": phone_number
        }
    }
    # Make a POST request to Mailchimp:
    r = requests.post(
        url=url,
        json=data,
        # We use the API key as password for authentication:
        auth=("SunriseNortheastern", api_key)
    )
    # If the request goes OK, print SUCCESS
    if r.ok:
        print("SUCCESSFULLY ADDED NEW SUBSCRIBER:", email_address)
    # Otherwise, print ERROR
    else:
        print("ERROR: FAILED TO ADD NEW SUBSCRIBER:", email_address)
        print(r.text)
    # NOTE: Sometimes, it's OK if an error occurs here!
    # For example, if someone fills out the Sunrise Sips form,
    # but they are already on our mailing list,
    # then Mailchimp will refuse to add them as a new subscriber.

def get_keys_and_ids():
    """
    Get API keys and secret IDs of Mailchimp audience, Google Sheets
    """
    # Get our Mailchimp API Key:
    api_key = None
    with open("api_key.txt", "r") as file:
        api_key = file.read()
    # Get the List ID of our Mailchimp audience:
    list_id = None
    with open("list_id.txt", "r") as file:
        list_id = file.read()
    # Get the ID of the Google spreadsheet
    spreadsheet_id = None
    with open("spreadsheet_id.txt", "r") as file:
        spreadsheet_id = file.read()
    # Get the range we want to read from in the Google spreadsheet:
    spreadsheet_range = None
    with open("spreadsheet_range.txt", "r") as file:
        spreadsheet_range = file.read()
        
    return api_key, list_id, spreadsheet_id, spreadsheet_range

def get_google_creds():
    """
    Get the user's Google credentials from the token.pickle file.
    If the token.pickle file does not exist,
    ask the user log into Google in their Web browser.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            
    return creds

def main():
    # Get relevant credentials:
    api_key, list_id, spreadsheet_id, spreadsheet_range = get_keys_and_ids()
    creds = get_google_creds()
    # Initialize Google Sheets API:
    service = build('sheets', 'v4', credentials=creds)

    # Get the values from the specified range in the spreadsheet:
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=spreadsheet_range
    ).execute()
    values = result.get('values', [])

    # Print an error message if no data is found:
    if not values:
        print("ERROR: DATA NOT FOUND")
    else:
        # Get the number of rows of the spreadsheet
        # we have processed so far
        # using the local "offset.txt" file.
        # This file will be updated at the end of our script.
        offset = None
        with open("offset.txt", "r") as file:
            offset = int(file.read())
        
        # For every row we have not yet processed, add a subscriber:
        for row in values[offset:]:
            add_subscriber(
                list_id,
                api_key,
                email_address=row[8],
                first_name=row[1],
                last_name=row[2],
                phone_number=row[9]
            )
        
        # Update the number of rows of the spreadsheet
        # we have processed so far:
        with open("offset.txt", "w") as file:
            file.write(str(len(values)))
        
        # Notify the user if there were no new subscribers to process:
        if offset == len(values):
            print("No new subscribers to add")
        # Otherwise, tell the user that we've finished adding subscribers:
        else:
            print("Finished adding subscribers")

if __name__ == '__main__':
    main()