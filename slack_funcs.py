import requests

def get_slack_token():
    """
    Gets the OAuth Slack Token from slack_token.txt
    """
    with open("slack_token.txt", "r") as file:
        return file.read()

def next_cursor(obj):
    """
    Given a JSON object returned by the Slack API,
    return the cursor to the next page,
    or None if there is no next cursor
    """
    # Return None if the cursor is non-existent:
    if "response_metadata" not in obj: return None
    if "next_cursor" not in obj["response_metadata"]: return None
    
    # Return None if the cursor is empty or null
    cursor = obj["response_metadata"]["next_cursor"]
    if cursor == "" or cursor == None: return None
    # Otherwise, just return the cursor:
    return cursor

def create_channel(api_token, channel_name):
    """
    Given a channel name, tries to create a Slack channel with that name
    """
    req = requests.post(
        url="https://slack.com/api/conversations.create",
        data={
            "token": api_token,
            "name": channel_name
        }
    )
    if req.ok and req.json()["ok"]:
        return
    else:
        raise RuntimeError(req.json())

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

def find_channel_id(api_token, channel_name):
    """
    Given a channel name, find the corresponding channel ID
    """
    # This cursor holds a token that allows us
    # to browse the next page of channels:
    cursor = None
    # To get the channel ID, we need to loop through all the channels,
    # so use an infinite loop:
    while True:
        # This is the data we will send to Slack
        # in order to browse the next page of channels:
        request_data = {
            "token": api_token,
            "types": "private_channel"
        }
        # Add the cursor if it is not None:
        if cursor != None:
            request_data["cursor"] = cursor
            
        # Get the next page of channels:
        req = requests.post(
            url="https://slack.com/api/conversations.list",
            data=request_data
        )
        # If the request is successful:
        if req.ok and req.json()["ok"]:
            response_data = req.json()
            # Loop through the channels:
            for channel in response_data["channels"]:
                # Return the channel ID if this is the right channel:
                if channel["name"] == channel_name:
                    return channel["id"]
            
            # If we fail to find the right channel, get the next cursor:
            cursor = next_cursor(response_data)
            # If the cursor is None,
            # then there are no more channels,
            # so raise an error:
            if cursor == None:
                raise RuntimeError("No channel named "+channel_name)
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

def join_channel(api_token, channel_id):
    """
    Given a channel ID, join the channel
    """
    req = requests.post(
        url="https://slack.com/api/conversations.join",
        data={
            "token": api_token,
            "channel": channel_id
        }
    )
    if req.ok and req.json()["ok"]:
        return
    else:
        raise RuntimeError(req.json())

def post_message_using_id(api_token, channel_id, message, username=""):
    """
    Given a channel ID, post a message to that channel
    under the given username
    """
    req = requests.post(
        url="https://slack.com/api/chat.postMessage",
        data={
            "token": api_token,
            "channel": channel_id,
            "text": message,
            "username": username
        }
    )
    if req.ok and req.json()["ok"]:
        return
    else:
        raise RuntimeError(req.json())

def post_message_in_channel(api_token, channel_name, message, username=""):
    """
    Given a Slack channel name,
    posts a message in that channel
    under the given username (if given)
    
    Assumes the bot is already part of the given channel
    """
    # Get the channel ID:
    channel_id = find_channel_id(api_token, channel_name)
    # Post the message in the channel:
    post_message_using_id(api_token, channel_id, message, username)

def send_dm_to_users(api_token, emails, message, username=""):
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
    post_message_using_id(api_token, im_channel_id, message, username)

def interactive_send_dm():
    """
    Sends a DM to a Slack user based off information from user input
    """
    email = input("Enter the e-mail of the user you want to DM: ")
    username = input("Enter the username you would like to DM them as: ")
    message = input("Enter the message you would like to DM them: ")
    
    slack_token = get_slack_token()
    send_dm_to_users(slack_token, [email], message, username)
    print("Message sent successfully")

def interactive_post_message_in_channel():
    """
    Posts a message in a Slack channel
    based off information from user input
    """
    channel = input("Enter the name of the channel you want to message: ")
    username = input("Enter the username you would like to send the message as: ")
    message = input("Enter the message you would like to send: ")
    
    slack_token = get_slack_token()
    post_message_in_channel(slack_token, channel, message, username)
    print("Message sent successfully")

if __name__ == "__main__":
    interactive_post_message_in_channel()