# Interest Form and Sunrise Sips Automation

This repo hosts a Python script which has two purposes:
 * Automatically add anyone who fill out the Sunrise Northeastern Interest Form to our Mailchimp
 * Automatically notify team leads if someone fills out the Interest Form expresses interest in their team and expresses interest in a Sunrise Sips conversation

This script works by reading the responses to the Interest Form in a Google Sheets and then making the appropriate requests to the Mailchimp and Slack APIs. To run this script, you first need to install some packages from `pip` by running the terminal command `pip install -r requirements.txt` in the directory containing the code from this repo.

Second, you need to make sure you have all of the appropriate text files necessary to run the script.

The following text files are not included in this repo because they contain privileged information, but they are still necessary to run this script:
 * `leadership_emails.json` holds the e-mails of the team leads that are notified when someone fills out the interest form
 * `google_credentials.json` holds the client ID and private key for a service account on our Google API Console project
 * `google_sheets_id.txt` holds the spreadsheet ID of the Google Sheets containing all of the form responses
 * `mailchimp_api_key.txt` holds the Mailchimp API Key
 * `mailchimp_list_id.txt` holds the list ID for our Mailchimp audience
 * `slack_token.txt` holds the OAuth access token for our Slack bot

If you want access to the files above, join Sunrise NEU's data team and ask leadership.

Once you have all of the files listed above, to run the script, simply run `python3 main.py` in the terminal.