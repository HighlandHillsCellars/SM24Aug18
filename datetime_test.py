# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 14:43:49 2018

@author: Rich
"""

from datetime import datetime,timedelta


#now = datetime.now()
timestr = "04/24/18 14:11"
now = datetime.strptime(timestr, "%m/%d/%y %H:%M")

print ("Today: ", now)
print ("Yesterday: ", now - timedelta(days=1))
print ("Day before Yesterday: ", now - timedelta(days=2))

print ("Tomorrow: ", now + timedelta(days=1))
print ("Day after Tomorrow: ", now + timedelta(days=2))


print ("1 week ago: ", now - timedelta(weeks=1))
print ("1 week from now: ", now + timedelta(weeks=1))

# Calculating a 15 day trial period
trial_started = datetime.now()
trial_ends = trial_started + timedelta(days=14)
print ("Started Trial on ", trial_started)
print ("Trial Ends  ", trial_ends)
print ("Trial Expires in  ", trial_ends - now)