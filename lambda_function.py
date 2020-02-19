import os
import json
import secretmanager
import trello
import slack
import boto3
from base64 import b64decode

def get_secret(name):
    return boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.getenv(name)))['Plaintext'].decode('utf-8')


def lambda_handler(event, context):
    trello_api_key = get_secret('TRELLO_API_KEY')
    trello_api_token = get_secret('TRELLO_API_TOKEN')
    trello_board_id = os.getenv('TRELLO_BOARD_ID')
    report_title = os.getenv('REPORT_TITLE')
    slack_api_token = get_secret('SLACK_API_TOKEN')
    slack_channel_id = os.getenv('SLACK_CHANNEL_ID')

    text = trello.create_report(
        trello_api_key, trello_api_token, trello_board_id, report_title)
    return {
        'statusCode': 200,
        'body': slack.post(slack_api_token, slack_channel_id, text)
    }
