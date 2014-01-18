eve-tower-alerter-gae
=====================

This project uses the Eve Online API to look for Tower Alert notifications and sends notifications.

Todo
----
*  Notifications do not seem to go away after I pull them.  This may be a caching issue.
*  Alerts are only printed out. No emails are actually sent.
*  Move the project to the Google App Engine and use a cron.yaml to schedule notification checks.

Sample Output
-------------
    Found Relavent Notification! 44919XXXX 75 100XXXX 1390068060 0
    Sending email to...
    To: blabblah@blahblah.com
    Subject: EVE Online Alert!
    Body:
    Notification ID: 44919XXXX
    Notification Type: tower_alert 75
    Sender ID: 100XXXX Date Sent: Sat Jan 18 10:01:00 2014
    Notification:
    aggressorAllianceID: null
    aggressorCorpID: 1000066
    aggressorID: 129701XXXX
    armorValue: 1.0
    hullValue: 1.0
    moonID: 4041XXXX
    shieldValue: 0.9966237833682771
    solarSystemID: 3100XXXX
    typeID: 17176

------