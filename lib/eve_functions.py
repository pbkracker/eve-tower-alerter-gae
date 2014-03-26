#!/usr/bin/python2.7
import time

# Just for debugging. Remove for GAE.
#sys.path.append("/usr/local/lib/python2.7/site-packages")
import sys
sys.path.append('lib/eveapi-1.2.6/')

import eveapi
import ConfigParser


def read_config():
  Config = ConfigParser.ConfigParser()
  Config.read("config.ini")
  accounts = {}
  noti_types = {}
  for section in Config.sections():
    if section.startswith("Account"):
      account = section
      accounts[account] = {
        "key_id": Config.get(account, "key_id"),
        "v_code": Config.get(account, "v_code"),
        "email": Config.get(account, "email")
      }
    elif section == 'NotificationTypes':
      typeIDs = Config.get(section, "typeIDs").split(",")
      notiNames = Config.get(section, "notiNames").split(",")
      index = 0
      for typeID in typeIDs:
        noti_types[int(typeID)] = notiNames[index]
        index = index + 1
    elif section == 'DeveloperEmail':
      developer_email = Config.get(section, "email")
  return accounts, noti_types, developer_email


def get_notification_headers(accounts):
  api = eveapi.EVEAPIConnection()
  notifications = {}
  for account in accounts:
    auth = api.auth(
      keyID=accounts[account]["key_id"],
      vCode=accounts[account]["v_code"])
    result2 = auth.account.Characters()
    notifications[account] = {}
    for character in result2.characters:
      notifications[account][character.characterID] = {}
      result = auth.char.Notifications(
        characterID=character.characterID)
      result = result.notifications
      for notid, typeid, senderid, sentdate, read in result.Select(
        'notificationID', 'typeID', 'senderID', 'sentDate', 'read'):
        notifications[account][character.characterID][notid] = {
          'notificationID': notid,
          'typeID': typeid,
          'senderID': senderid,
          'sentDate': sentdate,
          'read': read
        }
  return notifications


def filter_notification_headers(notifications, noti_types):
  # [account][characterID][notificationID] = {
  #   'notificationID': notid,
  #   'typeID': typeid,
  #   'senderID': senderid,
  #   'sentDate': sentdate,
  #   'read': read
  # }

  # n_headers = {}
  ignore_list = []
  for account in notifications:
    for character in notifications[account]:
      for notid in notifications[account][character]:
        n_struct = notifications[account][character][notid]
        if n_struct['typeID'] not in noti_types.keys():
          print "Ignoring Notification because of type. {}".format(n_struct)
          ignore_list.append((account, character, notid))
          continue
        print "Found Relavent Notification! {}".format(n_struct)
        n_struct['typeName'] = noti_types[n_struct['typeID']]

        # if not n_headers.has_key(account):
        #   n_headers[account] = {}
        # if not n_headers[account].has_key(character):
        #   n_headers[account][character] = str(notid)
        # else:
        #   n_headers[account][character] += ",{}".format(str(notid))

  for (account, character, notid) in ignore_list:
    del notifications[account][character][notid]

  return notifications


def retrieve_full_notification_text(accounts, notifications):
  # [account][characterID][notificationID] = {
  #   'notificationID': notid,
  #   'typeID': typeid,
  #   'senderID': senderid,
  #   'sentDate': sentdate,
  #   'read': read
  ##  'text': "blah blah blah"
  # }

  api = eveapi.EVEAPIConnection()
  for account in notifications:
    auth = api.auth(keyID=accounts[account]["key_id"], vCode=accounts[account]["v_code"])
    for character in notifications[account]:
      if len(notifications[account][character].keys()) > 0:
        comma_sep_ids = ",".join([str(b) for b in notifications[account][character].keys()])
        result = auth.char.NotificationTexts(characterID=character, IDs=comma_sep_ids)
        result_rowset = result.notifications
        for notid in notifications[account][character]:
          result_row = result_rowset.Get(int(notid))
          notifications[account][character][notid]['text'] = result_row['data']

  return notifications


def prepare_alerts(accounts, notifications):
  # [account][characterID][notificationID] = {
  #   'notificationID': notid,
  #   'typeID': typeid,
  #   'senderID': senderid,
  #   'sentDate': sentdate,
  #   'read': read
  ##  'text': "blah blah blah"
  # }
  messages = {}
  for account in notifications:
    messages[account] = {}
    messages[account]['to'] = accounts[account]['email']
    messages[account]['subject'] = "EVE Online Alert!"
    messages[account]['body'] = ""
    for character in notifications[account]:
      for notid in notifications[account][character]:
        notification = notifications[account][character][notid]
        messages[account]['body'] += "Notification ID: {}\n".format(notid)
        messages[account]['body'] += "Notification Type: {} {}\n".format(
          notification['typeName'], notification['typeID'])
        messages[account]['body'] += "Sender ID: {} Date Sent: {}\n".format(
          notification['senderID'], time.asctime(time.localtime(notification['sentDate'])))
        messages[account]['body'] += "Notification:\n{}\n------\n".format(notification['text'])
    if messages[account]['body'] == "":
      del messages[account]
    else:
      print "Sending email to..."
      print "To: {}".format(messages[account]['to'])
      print "Subject: {}".format(messages[account]['subject'])
      print "Body:\n{}".format(messages[account]['body'])
      print "\n\n"
  return messages

if __name__ == "__main__":
  accounts, noti_types = read_config()
  notifications = get_notification_headers(accounts)
  notifications = filter_notification_headers(notifications, noti_types)
  notifications = retrieve_full_notification_text(accounts, notifications)
  messages = prepare_alerts(accounts, notifications)
  import json
  print(json.dumps(messages, indent=2))


