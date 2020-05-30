# Interest Form and Sunrise Sips Automation

This repo hosts a Python script which has two purposes:
 * Automatically add anyone who fill out the Sunrise Northeastern Interest Form to our Mailchimp
 * Automatically notify team leads if someone fills out the Interest Form expresses interest in their team and expresses interest in a Sunrise Sips conversation

The `Code.gs` script works by running as a [Google Apps Script](https://developers.google.com/apps-script) which runs whenever someone submits the interest form. For security reasons, the following variables have been redacted from the code:

 * `LEADERSHIP_EMAILS` is a JSON object which maps team names to lists of e-mails of the people who lead that team
 * `MAILCHIMP_API_KEY` is a String containing our Mailchimp API key
 * `MAILCHIMP_LIST_ID` is a String containing the list ID of our Mailchimp audience
 * `SLACK_TOKEN` is a String containing our Slack bot user OAuth access token
 * `SLACK_WEBHOOK` is a String containing our Slack Webhook URL

If you want access to the spreadsheet which this script runs on, join Sunrise NEU's data team and ask leadership.

If you would like to see an older version of this code, which was a Python script that used the Google Sheets API, see [this commit](https://github.com/SunriseNortheastern/SunriseSips/tree/e9c4844095d487e45c636056a08056c35e44e05b).