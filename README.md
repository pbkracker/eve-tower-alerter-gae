eve-tower-alerter-gae
=====================

This project uses the Eve Online API to look for Tower Alert notifications and sends email alerts.
It runs in the Google App Engine.

The cron.yaml instructs google to hit /check once every 30 minutes.  The handler that responds to requests to /check then talks to the eve API to determine if there are any notifications, and sends out emails.

Move sample_config.ini to config.ini and fill in your values.

Sample Output
-------------
    ./eve_functions.py
    # This file can be run on the command line or used as a library.
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
