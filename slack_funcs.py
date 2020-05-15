import requests

def get_slack_token():
    """
    Gets the OAuth Slack Token from slack_token.txt
    """
    with open("slack_token.txt", "r") as file:
        return file.read()

def find_user_id(api_token, email):
    """
    Given a user's email, finds their user ID in Slack
    """
    req = requests.post(
        url="https://slack.com/api/users.lookupByEmail",
        data={
            "token": api_token,
            "email": email
        }
    )
    if req.ok and req.json()["ok"]:
        return req.json()["user"]["id"]
    else:
        raise RuntimeError(req.json())

def find_im_channel_id(api_token, user_ids):
    """
    Given a list of user IDs, find the IM channel ID of their group DM
    """
    req = requests.post(
        url="https://slack.com/api/conversations.open",
        data={
            "token": api_token,
            "users": ",".join(user_ids)
        }
    )
    if req.ok and req.json()["ok"]:
        return req.json()["channel"]["id"]
    else:
        raise RuntimeError(req.json())

def post_message(api_token, channel_id, username, message):
    """
    Given a channel ID, post a message to that channel
    under the given username
    """
    req = requests.post(
        url="https://slack.com/api/chat.postMessage",
        data={
            "token": api_token,
            "channel": channel_id,
            "username": username,
            "text": message
        }
    )
    if req.ok and req.json()["ok"]:
        return
    else:
        raise RuntimeError(req.json())

def send_dm_to_users(api_token, message, emails, username=""):
    """
    Given a list of e-mails,
    sends a group DM to all users with the given e-mails
    under the given username (if given)
    """
    # Get all of the user IDs corresponding to the given e-mails:
    user_ids = []
    for email in emails:
        user_ids.append(find_user_id(api_token, email))
    # Get the channel ID of the group DM:
    im_channel_id = find_im_channel_id(api_token, user_ids)
    # Send a message in the group DM:
    post_message(api_token, im_channel_id, username, message)

if __name__ == "__main__":
    email = input("Enter the e-mail of the user you want to DM: ")
    username = input("Enter the username you would like to DM them as: ")
    message = input("Enter the message you would like to DM them: ")
    
    slack_token = get_slack_token()
    send_dm_to_users(slack_token, message, [email], username)
    print("Message sent successfully")