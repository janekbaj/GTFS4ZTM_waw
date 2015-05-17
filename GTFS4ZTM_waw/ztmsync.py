'''
Created on Apr 20, 2015

@author: janbajerski
'''

import os
from ftplib import FTP
import datetime

def sync_files(local_dir):
    now = datetime.datetime.now()
    
    current_day = int(now.strftime("%y%m%d"))
    
    h_local_files = [] # create local dir list
    h_remote_files = [] # create remote dir list
    
    h_local= local_dir+'/sync';
    
    ftp = FTP('rozklady.ztm.waw.pl')
    ftp.login()
    
    if os.listdir(h_local) == []:
        print 'LOCAL DIR IS EMPTY'
    else:
        print 'BUILDING LOCAL DIR FILE LIST...'
        for file_name in os.listdir(h_local):
            h_local_files.append(file_name) # populate local dir list
    
    # ftp.sendcmd('CWD /some/ftp/directory')
    print 'BUILDING REMOTE DIR FILE LIST...\n'
    for rfile in ftp.nlst():
        if rfile.endswith('.7z'): # i need only .jpg files
            
            if (int(rfile[2:8]) >= current_day):
                h_remote_files.append(rfile) # populate remote dir list
    
    h_diff = sorted(list(set(h_remote_files) - set(h_local_files))) # difference between two lists
    
    
    for h in h_diff:
        with open(os.path.join(h_local,h), 'wb') as ftpfile:
            s = ftp.retrbinary('RETR ' + h, ftpfile.write) # retrieve file
            print 'PROCESSING', h
            if str(s).startswith('226'): # comes from ftp status: '226 Transfer complete.'
                print 'OK\n' # print 'OK' if transfer was successful
            else:
                print s # if error, print retrbinary's return
    
    return h_remote_files
   