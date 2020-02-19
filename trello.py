import requests
import os
import sys
from datetime import datetime
from pytz import timezone
import logging

trello_endpoint = "https://api.trello.com/1"

def create_report(key, token, board_id, report_title):
    trello_credential = {"key": key, "token": token}
    now = datetime.now(timezone('Asia/Tokyo'))

    # Fetch list ids on board.
    done_list_id = ""
    doing_list_id = ""

    board_lists = requests.get(trello_endpoint + "/boards/" +
                            board_id + "/lists", params=trello_credential).json()
    for list in board_lists:
        if list['name'] == 'Done':
            done_list_id = list['id']
        if list['name'] == 'Doing':
            doing_list_id = list['id']

    if done_list_id == "" or doing_list_id == "":
        logging.error(
            "Failed to get list_id on board_id[" + board_id + "].")
        sys.exit(1)

    # Fetch member ids on board.
    members = requests.get(trello_endpoint + "/boards/" + board_id +
                        "/members", params=trello_credential).json()
    memberidmap = {}
    for member in members:
        memberidmap[member['id']] = member['fullName']

    # Fetch cards from Done list.
    output = "```\n# " + now.strftime('%Y/%m/%d') + " " + report_title
    output += "\n\n## Done"
    cards = requests.get(trello_endpoint + "/lists/" + done_list_id +
                        "/cards", params=trello_credential).json()

    for card in cards:
        date_last_activity = datetime.strptime(
            card['dateLastActivity'], '%Y-%m-%dT%H:%M:%S.%f%z')
        if (now - date_last_activity).days < 7:
            membername = []
            for j in card['idMembers']:
                membername.append(memberidmap[j])
            output += "\n- (" + date_last_activity.strftime('%m/%d') + ") " + \
                card['name'] + " " + str(membername).replace("'", "")
        else:
            params = {"key": key, "token": token, "closed": "true"}
            res = requests.put(trello_endpoint + "/cards/" + card['id'],params=params)
            logging.warning(res.text)
            
    # Fetch cards from Doing list.
    output += "\n\n## Doing"
    cards = requests.get(trello_endpoint + "/lists/" + doing_list_id +
                        "/cards", params=trello_credential).json()

    for card in cards:
        membername = []
        for j in card['idMembers']:
            membername.append(memberidmap[j])
        output += "\n- " + card['name'] + " " + str(membername).replace("'", "")

    output += "\n```"
    return output
