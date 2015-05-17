'''
Created on Apr 20, 2015

'''

import datetime
import ztmsync 
import parse
import os

now = datetime.datetime.now()

x= int(now.strftime("%y%m%d"))

print x+1

local_dir = '.'

if not os.path.exists(local_dir + "/target"):
        os.makedirs(local_dir + "/target") 

if not os.path.exists(local_dir + "/sync"):
        os.makedirs(local_dir + "/sync") 

if not os.path.exists(local_dir + "/debug"):
        os.makedirs(local_dir + "/debug") 

processed_files  = ztmsync.sync_files(local_dir)


for f in processed_files:
    print f[:8]
    
    parse.parse_file(local_dir, f[:8])
