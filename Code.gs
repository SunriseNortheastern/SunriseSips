var LEADERSHIP_EMAILS = {
    "REDACTED": []
};

var MAILCHIMP_API_KEY = "REDACTED";
var MAILCHIMP_LIST_ID = "REDACTED";
var MAILCHIMP_CREDENTIALS = Utilities.base64Encode("SunriseNortheastern:"+MAILCHIMP_API_KEY);

var SLACK_TOKEN = "REDACTED";
var SLACK_WEBHOOK = "REDACTED";

//Logs a message in the given sheet:
function logMsg(msg) {
  SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Bot Logs").appendRow([new Date(), msg]);
}

//Given an e-mail, returns the user ID of the Slack user registered with that e-mail:
function findUserId(email) {
  var response = UrlFetchApp.fetch(
    "https://slack.com/api/users.lookupByEmail",
    {
      "method": "post",
      "payload": {
        "token": SLACK_TOKEN,
        "email": email
      }
    }
  );
  
  var responseData = JSON.parse(response.getContentText());
  return responseData.user.id;
}

function main() {
  //Get the offset from the Bot Data sheet:
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var offsetSheet = ss.getSheetByName("Bot Data");
  var offset = offsetSheet.getDataRange().getValues()[0][0];
  
  //Keep reading rows from the form data sheet,
  //starting at the index offset from above, and stopping when we hit an empty row
  var formDataSheet = ss.getSheetByName("Form Responses 1");
  var formDataValues = formDataSheet.getDataRange().getValues();
  while (formDataValues[offset]) {
    var row = formDataValues[offset];
    
    //This is the data we need to send to Mailchimp to add people to the mailing list:
    var mailchimpURL = "https://us4.api.mailchimp.com/3.0/lists/"+MAILCHIMP_LIST_ID+"/members";
    var mailchimpData = {
      "email_address": row[8],
      "status": "subscribed",
      "merge_fields": {
        "FNAME": row[1],
        "LNAME": row[2],
        "PHONE": row[9]
      }
    };
    var mailchimpHeaders = {
      "Authorization": "Basic "+MAILCHIMP_CREDENTIALS
    };
    //Try to add them to the mailing list using a POST request:
    UrlFetchApp.fetch(
      mailchimpURL,
      {
        "method": "post",
        "contentType": "application/json",
        "payload": JSON.stringify(mailchimpData),
        "headers": mailchimpHeaders,
        //This might give a 400 error if the user is already on the mailing list,
        //so mute HTTP errors:
        "muteHttpExceptions": true
      }
    );
    
    //List of team names we should mention in the Slack message:
    var teamNames = [];
    //Dictionary containing the user IDs we should mention in the Slack message:
    var importantIds = {};
    //Loop through the teams:
    Object.keys(LEADERSHIP_EMAILS).forEach(function(teamName) {
      //If the user is interested in this team, add the team name, and all of the user IDs of the leadership of this team:
      if (row[6].indexOf(teamName) > -1) {
        teamNames.push(teamName);
        for (var i = 0; i < LEADERSHIP_EMAILS[teamName].length; i++) {
          var email = LEADERSHIP_EMAILS[teamName][i];
          importantIds[findUserId(email)] = true;
        }
      }
    });
    
    //Add each user ID to the mentions at the beginning of the message:
    var slackMessage = "";
    Object.keys(importantIds).forEach(function(userId) {
      slackMessage += "<@"+userId+"> ";
    });
    slackMessage += "\n";
    
    //Add some more info about this person to the Slack message:
    slackMessage += row[1]+" "+row[2]+" filled out the interest form!\n";
    slackMessage += "\n";
    slackMessage += "Pronouns: "+row[3]+"\n";
    slackMessage += "Year: "+row[4]+"\n";
    slackMessage += "Major: "+row[5]+"\n";
    slackMessage += "Interests: "+teamNames.join(", ");
    slackMessage += "\n";
    slackMessage += "Interested in Sunrise Sips? "+row[7]+"\n";
    slackMessage += "E-mail: "+row[8]+"\n";
    slackMessage += "Phone Number: "+row[9]+"\n";
    slackMessage += "Best Method of Contact: "+row[12]+"\n";
    if (row[10].length > 0) {
      slackMessage += "\n";
      slackMessage += "Questions/Comments: "+row[10]+"\n";
    }
    slackMessage += "\n";
    slackMessage += "Sign up to do a Sunrise Sips here: https://docs.google.com/spreadsheets/d/"+ss.getId()+"/edit";
    
    
    //Post the Slack message:
    UrlFetchApp.fetch(
      SLACK_WEBHOOK,
      {
        "method": "post",
        "contentType": "application/json",
        "payload": JSON.stringify({"text": slackMessage})
      }
    );
    
    //Increment the offset variable in order to go to the next row:
    offset++;
  }
  offsetSheet.getRange("A1").setValue(offset);
}