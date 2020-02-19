import requests

slack_endpoint = "https://slack.com/api"

def post(token, channel_id, text):
    # Post to slack
    header = {'Content-Type': 'multipart/form-data; charset=utf-8'}
    data = {"token": token,
            "channel": channel_id, "text": text}
    response = requests.post(
        slack_endpoint + "/chat.postMessage", params=data, headers=header)
    return response.json()
