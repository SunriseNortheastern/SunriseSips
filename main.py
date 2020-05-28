import pickle
import os.path
from googleapiclient.discovery import build
from google.oauth2 import service_account
# Documentation: https://2.python-requests.org/en/master/
import requests
import slack_funcs
import json

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# This is the name of the Slack channel we message to notify team leads:
CHANNEL_NAME = "sunrisesips"

"""
This is the maximum number of rows of the spreadsheet
we are going to read in one run of this script.

For example, if MAX_ROWS is 10, but 20 new people have
signed up for Sunrise Sips since this script was last run,
then you would need to run this script twice to process
all of the new responses.

This constant exists because we are likely going to run
this script every minute or so, and therefore we never
want to have this script process so many responses at once
that it takes longer than a minute to finish.
"""
MAX_ROWS = 20

def get_mailchimp_info():
    """
    Return a tuple containing:
    - our Mailchimp API Key
    - the list ID of our Mailchimp audience
    """
    # Get our Mailchimp API Key:
    api_key = None
    with open("mailchimp_api_key.txt", "r") as file:
        api_key = file.read()
    # Get the List ID of our Mailchimp audience:
    list_id = None
    with open("mailchimp_list_id.txt", "r") as file:
        list_id = file.read()

    return api_key, list_id

def get_google_info():
    """
    Return a tuple containing:
    - the Google credentials needed to use the Google Sheets API
    - the spreadsheet ID of the Google Sheets
      containing all of the form responses
    """
    # Create the Credentials object using credentials.json:
    creds = service_account.Credentials.from_service_account_file(
        "google_credentials.json",
        scopes=SCOPES
    )

    # Get the ID of the Google Sheets containing the form responses:
    with open("google_sheets_id.txt", "r") as file:
        spreadsheet_id = file.read()

    return creds, spreadsheet_id

def add_subscriber(api_key, list_id, email_address, first_name="", last_name="", phone_number=""):
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
        print("FAILED TO ADD NEW SUBSCRIBER:", email_address)
        print(r.text)
    # NOTE: Sometimes, it's OK if an error occurs here!
    # For example, if someone fills out the Sunrise Sips form,
    # but they are already on our mailing list,
    # then Mailchimp will refuse to add them as a new subscriber.

def main():
    # Get relevant credentials:
    mailchimp_api_key, mailchimp_list_id = get_mailchimp_info()
    creds, spreadsheet_id = get_google_info()
    # Initialize Google Sheets API:
    service = build("sheets", "v4", credentials=creds)

    # Get the number of rows of the spreadsheet
    # we have processed so far
    # using the local "offset.txt" file.
    # This file will be updated at the end of our script.
    offset = None
    with open("offset.txt", "r") as file:
        offset = int(file.read())
    # Based off the offset, build the spreadsheet range we want to read:
    spreadsheet_range = f"Form Responses 1!A{offset}:V{offset+MAX_ROWS}"

    # Get the values from the specified range in the spreadsheet:
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=spreadsheet_range
    ).execute()
    values = result.get("values", [])

    # Log a message if there is no new data:
    if not values:
        print("No new subscribers")
    else:
        # Get the Slack token needed to access the Slack API:
        slack_token = slack_funcs.get_slack_token()
            
        # Get the e-mails of the team leads:
        with open("leadership_emails.json", "r") as file:
            team_lead_emails = json.loads(file.read())
            
        # Get the user IDs of all the team leads:
        team_lead_ids = {}
        for team_name, emails in team_lead_emails.items():
            team_lead_ids[team_name] = []
            for email in emails:
                team_lead_ids[team_name].append(
                    slack_funcs.find_user_id(slack_token, email)
                )
        
        # For every row we have not yet processed, add a subscriber:
        for row in values:
            add_subscriber(
                mailchimp_api_key,
                mailchimp_list_id,
                email_address=row[8],
                first_name=row[1],
                last_name=row[2],
                phone_number=row[9]
            )
            
            # Then, create a Slack message to notify the team leads:
            slack_message = \
f"""{row[1]} {row[2]} filled out the interest form!

Pronouns: {row[3]}
Year: {row[4]}
Major: {row[5]}
Interests: {{team_names}}

Interested in Sunrise Sips? {row[7]}
E-mail: {row[8]}
Phone Number: {row[9]}
Best Method of Contact: {row[11]}"""
            if len(row[10]) > 0:
                slack_message += f"\n\nQuestions/Comments: {row[10]}"
            slack_message += f"\n\nSign up to do a Sunrise Sips here: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"

            # Get the teams/people we need to mention:
            team_names = []
            people_to_be_mentioned = set()
            for team_name, ids in team_lead_ids.items():
                if team_name in row[6]:
                    team_names.append(team_name)
                    people_to_be_mentioned |= set(ids)
            # Put the team names that the user is interested in
            # in the message:
            slack_message = slack_message.format(
                team_names=", ".join(team_names)
            )
            # Prepend the mentions of each team lead to the message:
            mentions = ""
            for id in people_to_be_mentioned:
                mentions += "<@"+id+"> "
            slack_message = mentions+"\n"+slack_message

            # Finally, post the message:
            slack_funcs.post_message_in_channel(
                slack_token,
                channel_name=CHANNEL_NAME,
                message=slack_message
            )
        
        # Update the number of rows of the spreadsheet
        # we have processed so far:
        with open("offset.txt", "w") as file:
            file.write(str(offset+len(values)))
            
        print("Finished adding subscribers")

if __name__ == "__main__":
    main()