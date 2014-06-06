#!/usr/bin/python

import sys
import time
import serial
from optparse import OptionParser, make_option

print "Loading twitter library"
execfile("twt.py")

from random import choice

sales = ['Sales are up 64% since last year!',
'With this rate, we\'re going to run out of stock soon!',
'All I do is - vend, vend, vend - no matter what!',
'Veni, Vidi, Vendi!',
'NASDAQ, here we come!',
'Say hello to my little vend!',
'I made them an offer they couldn\'t refuse.',
'Machine, Vending Machine.',
'HAL ain\'t got nothing on me!',
'A cold beverage. Shaken, not stirred.',
'Hasta la venda, Baby!',
'Madness? This is BEVERAGES!',
'To vend, or not to vend. That is the question.',
'A day without vending is like a day without sunshine.',
'Ah, excellent, another valued customer!',
'Feeling overburdened by money?',
'A fantastic day for capitalism!',
'Luke, I am your father!']

dry =['Well that\'s enough to drink for today!',
'Whew, let me cool off for a minute.',
'It\'s not you - it\'s me.',
'It\'s time to kick ass and vend beverages - and I\'m all out of beverages!',
'I find my lack of beverages disturbing.']

undry =['Bring the big wallet, I\'m restocked!',
'Back on track, and ready to vend!']

jam =['Ugh - I don\'t feel so good.',
'I\'ll be back!',
'I just can\'t do it captain - I don\'t have the power!']

unjam =['I feel better already!',
'It\'s alive! It\'s alive!',
'Good as new, I think. Am I leaking?']

old_status = 'S0,J,D,C'

def tweet(str):
   try:
      response = client.api.statuses.update.post(status=str)
   except:
      print "Could not tweet " + str

def tweetStatus(type,i,action):
  if type == "S":
    tweet(choice(sales)+" (total vend count is now "+i[1:]+")")
  elif type == "D":
    if action == "add":
      tweet(choice(dry)+" (slot "+i+" is empty) @CUnnerup")
    else:
      tweet(choice(undry)+" (slot "+i+" refilled)")
  elif type == "J":
    if action == "add":
      tweet(choice(jam)+" (slot "+i+" jammed) @CUnnerup")
    else:
      tweet(choice(unjam)+" (slot "+i+" is no longer jammed)")
  elif type == "C":
    if action == "add":
       tweet("out of coins "+i)
    else:
       tweet("restocked coins "+i)

def updateStatus(str,old_str):
  if(str[0] == "S"):
    if(str != old_str):
      tweetStatus(str[0],str,"")
  else:
    l_added = list(set(str) - set(old_str))
    l_removed = list(set(old_str) - set(str))
    for item in l_added:
      tweetStatus(str[0],item,"add")
    for item in l_removed:
      tweetStatus(str[0],item,"rem")

def checkStatus(str):
  global old_status
  old_stat = old_status.split(",")
  stat = str.split(",")
  for index in range(len(stat)):
    if stat[index] != old_stat[index]:
      updateStatus(stat[index],old_stat[index]);

def parseStatus(stat):
  global old_status
  if old_status != stat:
    if old_status != '':
      checkStatus(stat)
    old_status = stat

while True:
  try:
    print "Trying to establish Bluetooth connection"
    ser = serial.Serial('/dev/rfcomm0') # Create serial port
  except:
    print "Could not initialize Bluetooth connection. Retrying."
    time.sleep(60)

  if ser.isOpen():
    print "Connection established."
    while True:
      time.sleep(2)
      try:
        sodaStatus = ser.read(ser.inWaiting())
        if sodaStatus:
          print "Data: " + sodaStatus
        #    parseStatus(sodaStatus)
        if ser.isOpen() == False:
          print "Connection closed."
          break
      except:
        print "Dropped Bluetooth connection unexpectedly."
        break
    print "Retrying..."