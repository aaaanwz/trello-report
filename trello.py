import requests
import os
import sys
from datetime import datetime
from pytz import timezone
import logging
import copy

trello_endpoint = "https://api.trello.com/1"


def create_report(key, token, board_id, report_title):
    trello_credential = {"key": key, "token": token}
    now = datetime.now(timezone('Asia/Tokyo'))

    # Fetch list ids on board.
    list_id = getListId(trello_credential, board_id)

    # Fetch member ids on board.
    memberidmap = getMembers(trello_credential, board_id)

    # Fetch cards from Done list.
    output = {"Title": now.strftime('%Y/%m/%d') + " " + report_title}
    output['Done'] = getCardsForEachLabels(
        trello_credential, board_id, list_id['Done'], memberidmap, now, True)
    output['Doing'] = getCardsForEachLabels(
        trello_credential, board_id, list_id['Doing'], memberidmap, now, False)
    return build_markdown_text(output)


def getCardsForEachLabels(trello_credential, board_id, list_id, memberidmap, now, archive):
    cards = requests.get(trello_endpoint + "/lists/" + list_id +
                         "/cards", params=trello_credential).json()
    result = {}
    for card in cards:
        date_last_activity = datetime.strptime(
            card['dateLastActivity'], '%Y-%m-%dT%H:%M:%S.%f%z')
        if (now - date_last_activity).days < 7:
            primary_label = 'その他' if not card['labels'] else card['labels'][0]['name']
            entry = result.get(primary_label)
            if entry != None:
                entry.append(cardToString(card, memberidmap))
                result[primary_label] = entry
            else:
                result[primary_label] = [
                    cardToString(card, memberidmap)]
        elif archive:
            archiveCard(trello_credential, card['id'])
    return result


def getListId(trello_credential, board_id):
    result = {}
    board_lists = requests.get(trello_endpoint + "/boards/" +
                               board_id + "/lists", params=trello_credential).json()
    for list in board_lists:
        result[list['name']] = list['id']
    return result


def getMembers(trello_credential, board_id):
    members = requests.get(trello_endpoint + "/boards/" + board_id +
                           "/members", params=trello_credential).json()
    memberidmap = {}
    for member in members:
        memberidmap[member['id']] = member['fullName']
    return memberidmap


def archiveCard(trello_credential, card_id):
    params = copy.deepcopy(trello_credential)
    params['closed'] = "true"
    res = requests.put(trello_endpoint + "/cards/" + card_id, params=params)
    logging.warning(res.text)


def cardToString(card, memberIdMap):
    result = card['name'] + " "
    memberName = []
    for memberId in card['idMembers']:
        memberName.append(memberIdMap[memberId])
    result += str(memberName).replace("'", "")
    return result

def build_markdown_text(obj):
    output = "# " + obj['Title'] + "\n"
    output += "\n## 完了🎉\n"
    for label in obj['Done']:
        output += "\n### " + label + "\n"
        for card in obj['Done'][label]:
            output += "- " + card + "\n"
    output += "\n## 作業中✍️\n"
    for label in obj['Doing']:
        output += "\n### " + label + "\n"
        for card in obj['Doing'][label]:
            output += "- " + card + "\n"
    return output
