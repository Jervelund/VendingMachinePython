#!/usr/bin/python

import sys
import time
import serial
from optparse import OptionParser, make_option

#print "Loading twitter library"
#execfile("twt.py")

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

def tweet(str):
  print "\nTweet: " + str + "\n"
  #try:
  #   response = client.api.statuses.update.post(status=str)
  #except:
  #   print "Could not tweet " + str

def tweetStatus(type,i,action):
  if type == 'B':
    tweet(choice(sales) + " (total vend count is now " + i + ")")
  elif type == 'D':
    if action == "add":
      tweet(choice(dry) + " (slot " + i + " is empty) @CUnnerup")
    else:
      tweet(choice(undry) + " (slot " + i + " refilled)")
  elif type == 'J':
    if action == "add":
      tweet(choice(jam) + " (slot " + i + " jammed) @CUnnerup")
    else:
      tweet(choice(unjam) + " (slot " + i + " is no longer jammed)")
  elif type == 'R':
    if action == "add":
       tweet("Out of coins " + i)
    else:
       tweet("Restocked coins " + i)
  elif type == 'C':
    tweet("Card swiped - current credits: " + i)

def tweetDiff(type, str, old_str):
  l_added = list(set(str) - set(old_str))
  l_removed = list(set(old_str) - set(str))
  for item in l_added:
    tweetStatus(type, item, "add")
  for item in l_removed:
    tweetStatus(type, item, "rem")

oldBuffer = {}
parseBuffer = ''

def parseStatus(stat):
  global parseBuffer

  parseBuffer += stat

  length = len(parseBuffer)

  if length == 0:
    return

  print "parseBuffer: " + parseBuffer

  if parseBuffer[0] == 'B': # Beverages dispensed
    if ',' in parseBuffer:
      if parseBuffer[1:parseBuffer.index(',')].isdigit():
        cmd = parseBuffer[1:parseBuffer.index(',')]
        #print "B: " + cmd
        if parseBuffer[0] in oldBuffer and cmd != oldBuffer[parseBuffer[0]]:
          tweetStatus(parseBuffer[0], cmd, '')
        oldBuffer[parseBuffer[0]] = cmd

        parseBuffer = parseBuffer[parseBuffer.index(',') + 1:]
    else:
      return
  elif parseBuffer[0] == 'J' or parseBuffer[0] == 'D' or parseBuffer[0] == 'R': # Jammed slots or empty beverage slots (dry) or empty coin return slots
    if ',' in parseBuffer:
      if parseBuffer[1:parseBuffer.index(',')].isdigit():
        cmd = parseBuffer[1:parseBuffer.index(',')]
        #print parseBuffer[0] + " " + cmd
        if parseBuffer[0] in oldBuffer:
          tweetDiff(parseBuffer[0], cmd, oldBuffer[parseBuffer[0]])
        oldBuffer[parseBuffer[0]] = cmd
        parseBuffer = parseBuffer[parseBuffer.index(',') + 1:]
    else:
      return
  elif parseBuffer[0] == 'C': # Credits in machine
    # 'Cxyxyxyxyxy'
    if len(parseBuffer) < 11:
      return
    value = str(ord(parseBuffer[1]) | (ord(parseBuffer[2]) << 8))
    #print "Value: " + value
    for i in range(3,11,2):
      if value != str(ord(parseBuffer[i]) | (ord(parseBuffer[i + 1]) << 8)):
        parseBuffer = parseBuffer[i:]
        parseStatus('')
        return

    tweetStatus(parseBuffer[0], value, '')
    parseBuffer = parseBuffer[11:]
  elif parseBuffer[0] == 'S': # Set current credits
    # 'Sxy'
    return
  elif parseBuffer[0] == 'E': # Error EEPROM bad
    # 'E'
    pass
  elif parseBuffer[0] == 'O': # Out of memory
    # 'O'
    # @Jervelund @Lauszus
    pass
  elif parseBuffer[0] == 'N': # No credit
    # 'N'
    pass

  #print "parseBuffer: " + parseBuffer

  if len(parseBuffer) == length:
    parseBuffer = parseBuffer[1:]
  parseStatus('')

def main():
  while True:
    try:
      print "Trying to establish Bluetooth connection."
      ser = serial.Serial('/dev/rfcomm0') # Create serial port
    except:
      print "Could not initialize Bluetooth connection. Retrying."
      time.sleep(10)

    if ser:
      if ser.isOpen():
        print "Connection established."
        while True:
          time.sleep(2)
          sodaStatus = ''
          try:
            sodaStatus = ser.read(ser.inWaiting())
          except:
            print "Dropped Bluetooth connection unexpectedly."
            break
          if sodaStatus:
            print "Data: " + sodaStatus
            parseStatus(sodaStatus)
        print "Retrying..."
        parseBuffer = ''
        if ser:
          ser.close()

main()