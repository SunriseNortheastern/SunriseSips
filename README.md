# Interest Form and Sunrise Sips Automation

This repo hosts a Python script which has two purposes:
 * Automatically add anyone who fill out the Sunrise Northeastern Interest Form to our Mailchimp
 * Automatically notify team leads if someone fills out the Interest Form expresses interest in their team and expresses interest in a Sunrise Sips conversation (not implemented yet)

This script works by reading the responses to the Interest Form in a Google Sheets and then making the appropriate requests to the Mailchimp and Slack APIs. To run the `main.py` script in this repo, you first need to install the below packages from `pip`:

```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib requests
```

The following text files are included in this repo and do not contain privileged information:
 * `offset.txt` holds a single integer that represents the number of rows in the spreadsheet that has already been processed by this script.

The following text files are not included in this repo because they contain privileged information, but they are still necessary to run this script:
 * `credentials.json` holds the client ID and client secret obtained by [enabling the Google sheets API on the Quickstart page](https://developers.google.com/sheets/api/quickstart/python)
 * `mailchimp_api_key.txt` holds the Mailchimp API Key
 * `list_id.txt` holds the list ID for our Mailchimp audience
 * `spreadsheet_id.txt` holds the spreadsheet ID of the Google Sheets containing all of the form responses

If you want access to the files above, join Sunrise NEU's data team and ask leadership!