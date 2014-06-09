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

def tweet(str):
  try:
     response = client.api.statuses.update.post(status=str)
     print "Sent tweet: " + str
  except:
     print "Could not tweet: " + str

def tweetStatus(type,i='',action=''):
  if type == ord('B'):
    tweet(choice(sales) + " (total vend count is now " + i + ")")
  elif type == ord('D'):
    if action == "add":
      tweet(choice(dry) + " (slot " + i + " is empty) @CUnnerup")
    else:
      tweet(choice(undry) + " (slot " + i + " refilled)")
  elif type == ord('J'):
    if action == "add":
      tweet(choice(jam) + " (slot " + i + " jammed) @CUnnerup")
    else:
      tweet(choice(unjam) + " (slot " + i + " is no longer jammed)")
  elif type == ord('R'):
    if action == "add":
       #tweet("Out of coins " + i)
       print "Out of coins " + i
    else:
       #tweet("Restocked coins " + i)
       print "Restocked coins " + i
  elif type == ord('C'):
    #tweet("Card swiped - current credits: " + i)
    print "Card swiped - current credits: " + i
  elif type == ord('F'):
    if action == 'deposit':
      #tweet("Card swiped - deposited: " + str(i))
      print "Card swiped - deposited: " + str(i)
    else:
      #tweet("Card swiped - withdrew: " + str(i))
      print "Card swiped - withdrew: " + str(i)
  elif type == ord('E'):
    if action == 0:
      tweet("Shoot! I'm really in trouble now - couldn't withdraw! :( (EEPROM  Error) @Jervelund @Lauszus @CUnnerup")
    else:
      tweet("Shoot! I'm really in trouble now - couldn't deposit. :( (EEPROM Error) @Jervelund @Lauszus @CUnnerup")
  elif type == ord('O'):
    tweet("Why can't I hold all these card UIDs. :( (EEPROM full) @Jervelund @Lauszus @CUnnerup")
  elif type == ord('N'):
    #tweet("I ain't saying I'm a gold digger, but I ain't messing with no empty cards. (No credit)")
    print "I ain't saying I'm a gold digger, but I ain't messing with no empty cards. (No credit)"
  elif type == ord('c'):
    #tweet("Added " + str(i) + " kr with coins")
    print "Added " + str(i) + " kr with coins"
  elif type == ord('r'):
    #tweet("Returned a " + str(i) + " kr coin")
    print "Returned a " + str(i) + " kr coin"
  else:
    tweet("Error! Unknown command: " + str(type) + " @Jervelund @Lauszus @CUnnerup")

def tweetDiff(type, str, old_str):
  l_added = list(set(str) - set(old_str))
  l_removed = list(set(old_str) - set(str))
  for item in l_added:
    tweetStatus(type, item, "add")
  for item in l_removed:
    tweetStatus(type, item, "rem")

oldBuffer = {}
parseBuffer = ''
if False: # Debug messages for all possible RFID transactions
  # Withdraw
  parseBuffer += 'CabababababN' # No credits
  parseBuffer += 'CabababababSxyF' # withdrew xy credits
  parseBuffer += 'CabababababE' # Bad EEPROM error
  # Deposit
  parseBuffer += 'CabababababZZZZZF' # Deposited ab credits
  parseBuffer += 'CabababababZZZZZSabE' # Could not deposit credits, due to bad EEPROM
  parseBuffer += 'CabababababZZZZZSabO' # Could not deposit credits, due to out of EEPROM

currentCreditsInMachine = 0
currentMode = 'withdraw'
setCredits = 0

def parseStatus(stat):
  global parseBuffer, currentMode, setCredits, currentCreditsInMachine, oldBuffer

  parseBuffer += stat
  length = len(parseBuffer)
  if length == 0:
    return

  cmd = ord(parseBuffer[0]) # Case sensitive matching

  if cmd == ord('B') or cmd == ord('J') or cmd == ord('D') or cmd == ord('R'): # Beverages dispensed or jammed slots or empty beverage slots (dry) or empty coin return slots
    if ',' in parseBuffer:
      indx = parseBuffer.index(',')
      if parseBuffer[1:indx].isdigit() or indx == 1:
        value = parseBuffer[1:indx]
        if cmd in oldBuffer and value != oldBuffer[cmd]:
          if cmd == ord('B'):
            tweetStatus(cmd, value, '')
          else:
            tweetDiff(cmd, value, oldBuffer[cmd])
        oldBuffer[cmd] = value
        parseBuffer = parseBuffer[indx + 1:]
    else:
      return
  elif cmd == ord('C'): # Credits in machine
    # 'Cxy_xy_xy_xy_xy_'
    if len(parseBuffer) < 16:
      return
    value = str(ord(parseBuffer[1]) | (ord(parseBuffer[2]) << 8))
    for i in range(4,16,3):
      if value != str(ord(parseBuffer[i]) | (ord(parseBuffer[i + 1]) << 8)):
        parseBuffer = parseBuffer[i:]
        parseStatus('')
        return # Stop if error detected with 'C' command
    # Set/reset state variables
    currentCreditsInMachine = value
    currentMode = 'withdraw'
    setCredits = 0

    parseBuffer = parseBuffer[16:]
  elif cmd == ord('S'): # Set current credits
    # 'Sxy'
    if len(parseBuffer) < 3:
      return
    value = str(ord(parseBuffer[1]) | (ord(parseBuffer[2]) << 8))
    setCredits = value
    parseBuffer = parseBuffer[3:]
  elif cmd == ord('E'): # Error EEPROM bad
    # 'E'
    tweetStatus(cmd, '', setCredits)
  elif cmd == ord('O'): # Out of memory
    # 'O'
    tweetStatus(cmd)
  elif cmd == ord('N'): # No credit
    # 'N'
    tweetStatus(cmd)
  elif cmd == ord('F'): # No credit
    # 'F'
    if currentMode == 'deposit':
      tweetStatus(cmd, currentCreditsInMachine, currentMode);
    else:
      tweetStatus(cmd, setCredits, currentMode);
  elif cmd == ord('Z'): # Credits zeroed - deposit mode
    # 'Z'
    currentMode = 'deposit'
  elif cmd == ord('c'): # coins added
    # 'cx' - byte encoded value
    if len(parseBuffer) < 2:
      return
    tweetStatus(cmd , ord(parseBuffer[1]))
    parseBuffer = parseBuffer[2:]
  elif cmd == ord('r'): # return coins
    # 'rx' - byte encoded value
    if len(parseBuffer) < 2:
      return
    tweetStatus(cmd , ord(parseBuffer[1]))
    parseBuffer = parseBuffer[2:]

  if len(parseBuffer) == length:
    parseBuffer = parseBuffer[1:]
  parseStatus('')

def main():
  while True:
    ser = ''
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
          sodaStatus = ''
          try:
            sodaStatus = ser.read(ser.inWaiting())
          except:
            print "Dropped Bluetooth connection unexpectedly."
            break
          if sodaStatus:
            parseStatus(sodaStatus)
          time.sleep(5)
        print "Retrying..."
        parseBuffer = ''
        if ser:
          ser.close()

main()