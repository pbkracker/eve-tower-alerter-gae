"""RequestHandlers"""

__author__ = 'opticrealm@gmail.com (Patrick Kelley)'

# Add the library location to the path
import sys
sys.path.insert(0, 'lib')

import webapp2
import eve_functions
import json
from copy import deepcopy
from google.appengine.ext import db
from google.appengine.api import mail


class EveTowerAlert(db.Model):
    """Keeps track of which notifications have been emailed."""
    nid = db.StringProperty()
    # has_been_sent = db.StringProperty()

# def reddit_key(): # entity_name=DEFAULT_ENTITY_GROUP_NAME
#     """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
#     return db.Key('RedditEntity')


class MainPage(webapp2.RequestHandler):

  def get(self):
    print "HAI THERE!"
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('Hello, World!')


class EveTowerAlerter(webapp2.RequestHandler):

  def _filter_by_requires_alert(self, notifications):
    """ Looks at the DB to see if we have already emailed this notification.
        If so, it removes it from the data structure.
    """
    # Using a deepcopy because you can't delete the datastructure
    # you are currently walking on. (or iterating over)
    edit_notifications = deepcopy(notifications)
    for account in notifications:
      for character in notifications[account]:
        for notid in notifications[account][character]:
          q = EveTowerAlert.all()
          q.filter("nid =", str(notid))
          already_exists = q.get()
          if already_exists:
            print "Ignoring {} because we've already alerted on it.".format(notid)
            del edit_notifications[account][character][notid]
    return edit_notifications

  def _send_alert_messages(self, messages, notifications, developer_email):

    for account in messages:
      # send email, then add DB entry
      mail.send_mail(developer_email,
                     messages[account]['to'],
                     messages[account]['subject'],
                     messages[account]['body'])
      for character in notifications[account]:
        for notid in notifications[account][character]:
          print "Adding {} to our DB so we dont send it again.".format(notid)
          eve_alert = EveTowerAlert()
          eve_alert.nid = str(notid)
          eve_alert.put()

  def get(self):
    accounts, noti_types, developer_email = eve_functions.read_config()
    notifications = eve_functions.get_notification_headers(accounts)
    notifications = self._filter_by_requires_alert(notifications)
    notifications = eve_functions.filter_notification_headers(
      notifications, noti_types)
    notifications = eve_functions.retrieve_full_notification_text(
      accounts, notifications)
    messages = eve_functions.prepare_alerts(accounts, notifications)
    self._send_alert_messages(messages, notifications, developer_email)

    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('Check Complete.\n')
    # self.response.write('Accounts:\n')
    # self.response.write(json.dumps(accounts, indent=2))
    # self.response.write('\n\nNotification Types:\n')
    # self.response.write(json.dumps(noti_types, indent=2))
    self.response.write("\n\nFull Notifications:\n")
    self.response.write(json.dumps(notifications, indent=2))
    self.response.write("\n\nMessages:\n")
    self.response.write(json.dumps(messages, indent=2))

application = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/check', EveTowerAlerter)
], debug=True)
