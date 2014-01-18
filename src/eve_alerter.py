#!/usr/bin/python2.7
import time
import sys
sys.path.append("../lib/python2.7/site-packages/eveapi-1.2.6/")

# Just for debugging. Remove for GAE.
#sys.path.append("/usr/local/lib/python2.7/site-packages")

import eveapi
import ConfigParser

def read_config():
  Config = ConfigParser.ConfigParser()
  Config.read("../config.ini")
  accounts = {}
  noti_types = {}
  for section in Config.sections():
    if section.startswith("Account"):
      account = section
      accounts[account] = {
        "key_id": Config.get(account,"key_id"),
        "v_code": Config.get(account,"v_code"),
        "email": Config.get(account,"email")
      }
    elif section == 'NotificationTypes':
      typeIDs = Config.get(section,"typeIDs").split(",")
      notiNames = Config.get(section,"notiNames").split(",")
      index=0
      for typeID in typeIDs:
        noti_types[int(typeID)] = notiNames[index]
        index = index + 1
  return accounts, noti_types

def get_notification_headers(accounts):
  api = eveapi.EVEAPIConnection()
  notifications = {}
  for account in accounts:
    auth = api.auth(keyID=accounts[account]["key_id"], vCode=accounts[account]["v_code"])
    result2 = auth.account.Characters()
    notifications[account] = {}
    for character in result2.characters:
      result = auth.char.Notifications(characterID=character.characterID)
      notifications[account][character.characterID] = result.notifications
      print notifications[account][character.characterID]
  return notifications

def filter_notification_headers(notifications, noti_types):
  # for each character, obtain a comma-separated list of notificationIDs
  n_headers = {}
  n_map = {}

  for account in notifications:
    for character in notifications[account]:
      result = notifications[account][character]
      for notid,typeid,senderid,sentdate,read in result.Select('notificationID', 'typeID', 'senderID', 'sentDate', 'read'):
        if typeid not in noti_types.keys():
          print "Ignoring Notification because of type. {} {} {} {} {}".format(notid,typeid,senderid,sentdate,read)
          continue
        # Found Relavent Notification! 449195420 75 1000137 1390068060 0
        print "Found Relavent Notification! {} {} {} {} {}".format(notid,typeid,senderid,sentdate,read)
        n_map[notid] = {"typeID": typeid, "typeName": noti_types[typeid], "senderID": senderid, "sentDate": sentdate}
        if not n_headers.has_key(account):
          n_headers[account] = {}
        if not n_headers[account].has_key(character):
          n_headers[account][character] = str(notid)
        else:
          n_headers[account][character] += ",{}".format(str(notid))

  return n_headers, n_map

def retrieve_full_notification_text(accounts, filtered_ids, n_map):
  full_notifications = {}

  api = eveapi.EVEAPIConnection()
  for account in filtered_ids:
    if not full_notifications.has_key(account):
        full_notifications[account] = {}
    auth = api.auth(keyID=accounts[account]["key_id"], vCode=accounts[account]["v_code"])
    # Example filtered_ids:
    # {'AccountOne': {1362910442: '449195420'}}
    # {'AccountOne': {1362910442: '449195420,449195421'}}
    for character in filtered_ids[account]:
      comma_sep_ids = filtered_ids[account][character]
      if not full_notifications[account].has_key(character):
        full_notifications[account][character] = {}
      result = auth.char.NotificationTexts(characterID=character, IDs=comma_sep_ids)
      result_rowset = result.notifications
      for notid in comma_sep_ids.split(','):
        result_row = result_rowset.Get(int(notid))
        result_dict = {
          "text": result_row['data'],
          "noti_typeID": n_map[int(notid)]["typeID"],
          "noti_name": n_map[int(notid)]["typeName"],
          "senderID": n_map[int(notid)]["senderID"],
          "sentDate": n_map[int(notid)]["sentDate"]
        }
        full_notifications[account][character][notid] = result_dict

  return full_notifications

def send_alerts(accounts, full_notifications):
  for account in full_notifications:
    message = {}
    message['to'] = accounts[account]['email']
    message['subject'] = "EVE Online Alert!"
    message['body'] = ""
    for character in full_notifications[account]:
      for notid in full_notifications[account][character]:
        notification = full_notifications[account][character][notid]
        message['body'] += "Notification ID: {}\n".format(notid)
        message['body'] += "Notification Type: {} {}\n".format(notification['noti_name'], notification['noti_typeID'])
        message['body'] += "Sender ID: {} Date Sent: {}\n".format(notification['senderID'], time.asctime(time.localtime(notification['sentDate'])))
        # Date Sent: 1390068060
        # Convert to something readable
        message['body'] += "Notification:\n{}\n------\n".format(notification['text'])
    print "Sending email to..."
    print "To: {}".format(message['to'])
    print "Subject: {}".format(message['subject'])
    print "Body:\n{}".format(message['body'])

if __name__ == "__main__":
  accounts, noti_types = read_config()
  notifications = get_notification_headers(accounts)
  filtered_ids, n_map = filter_notification_headers(notifications, noti_types)
  full_notifications = retrieve_full_notification_text(accounts, filtered_ids, n_map)
  send_alerts(accounts, full_notifications)

  
