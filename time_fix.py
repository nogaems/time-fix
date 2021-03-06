#!/usr/bin/env python
# coding: utf8

import ntplib
from time import ctime
import sys
from optparse import OptionParser
import os
import re
import platform as pltf
import datetime
import urllib2

platform = pltf.system()
if platform is 'Windows':
    os.system('cls')
else:
    os.system('clear')

usage = "Usage: %prog [options] arguments"
parser = OptionParser(usage)
parser.add_option("-p", "--pool", dest="pool",
                  help="Use the specified NTP-pool", metavar="POOL")
parser.add_option("-r", "--request", dest="request",
                  help="Time request only, does not change time", metavar="POOL")
parser.add_option("-a", "--autorun",action='store_true', dest="autorun", default=False, 
                  help="Add to autorun")
parser.add_option("-g", "--google", action='store_true', dest="google", default=False, 
                  help="Get the time by requesting Google")

(options, args) = parser.parse_args()

if options.google:
    url = 'https://www.google.ru/search?q=' + urllib2.quote('время')
    headers = {'Host': 'www.google.ru',
               'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:31.0) Gecko/20100101 Firefox/31.0 Iceweasel/31.8.0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language': 'en-US,en;q=0.5',
               'Accept-Charset': 'utf-8',
               'Connection': 'keep-alive',
               'Cache-Control': 'max-age=0'}
    req = urllib2.Request(url, headers = headers)
    print("Sent request to Google...")
    r = urllib2.urlopen(req)
    r = r.read()
    time = re.search('class="vk_bk vk_ans">(?P<time>.{5})</div>', r.decode('utf8')).groupdict()['time']
    print('Current time is {0}'.format(time))
    print("Setting the System Clock...")
    if platform == 'Linux':
        d = datetime.date.today().strftime('%Y-%m-%d') + ' ' + time
        os.system('hwclock --set --date="' + d + '"')
        os.system('hwclock --hctosys')
    else:
        os.system("time " + time)    
    print("Done.\n")
    sys.exit()

if not options.pool:
    pool = "ru.pool.ntp.org"
else:
    pool = options.pool
print("Used NTP-pool: {0}".format(pool))
print("Sent request...")

c = ntplib.NTPClient()
response = c.request(pool)
time = ctime(response.tx_time).split(" ")[3]
print(ctime(response.tx_time))

if options.request:
    print("Done.\n")
    sys.exit()

if options.autorun:
    os.system('pip install ntplib')
    if platform is 'Windows':
        reg = 'reg add HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run /v TimeFix /t REG_SZ /d %cd%\\time_fix.exe) /f'
        os.system(reg)
        print('Added in autostart.\nDone.')
        sys.exit()
    else:
        script = os.path.abspath(os.curdir) + '/time_fix.py'
        os.system('cp ' + script + ' /etc/init.d/time_fix.py')
        os.system('update-rc.d time_fix.py defaults')
        print('Added in autostart.\nDone.')
        sys.exit()

print("Setting the System Clock...")
if platform is 'Windows':
    os.system("time " + time)
    print("Done.\nPress any key...")
    input()
else:
    os.system('date -s \'' + ctime(response.tx_time) + '\'')
    print("Done.\n")
