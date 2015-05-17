
import py7zlib
import os
import md5
import re
import datetime
import shutil




class SevenZFileError(py7zlib.ArchiveError):
    pass

class SevenZFile(object):
    @classmethod
    def is_7zfile(cls, filepath):
        """ Determine if filepath points to a valid 7z archive. """
        is7z = False
        fp = None
        try:
            fp = open(filepath, 'rb')
            #archive = py7zlib.Archive7z(fp)
            is7z = True
        finally:
            if fp: fp.close()
        return is7z

    def __init__(self, filepath):
        fp = open(filepath, 'rb')
        self.filepath = filepath
        self.archive = py7zlib.Archive7z(fp)

    def __contains__(self, name):
        return name in self.archive.getnames()

    def bytestream(self, name):
        """ Iterate stream of bytes from an archive member. """
        if name not in self:
            raise SevenZFileError('member %s not found in %s' %
                                  (name, self.filepath))
        else:
            member = self.archive.getmember(name)
            for byte in member.read():
                if not byte: break
                yield byte

    def readlines(self, name):
        """ Iterate lines from an archive member. """
        linesep = os.linesep[-1]
        line = ''
        for ch in self.bytestream(name):
            line += ch
            if ch == linesep:
                yield line.decode("cp1250").encode('utf-8')
                line = ''
        if line: yield line.decode("cp1250").encode('utf-8')




def processTY(f,lines):
    print "Parsing section - TY - trips days"
    
    for line in f:
        if line[:1] == "#":
            break
    return False   
    
    
def processKA(f,lines): 
    global result_directory
    print "Parsing section - KA - calendar"  
    exception_file  = open(result_directory + '/calendar_dates.txt','w')
    exception_file.write("service_id,date,exception_type\n")
    for line in f:
        if line[:1] == "#":
            break
        fields = line.split()
        days = fields[3:]
        day = fields[0].split("-")
        weekday = datetime.date(int(day[0]),int(day[1]),int(day[2])).weekday()
        #print (fields[0] + " " + str(weekday))
        if weekday <5 :
            if (not "DP" in days):
                print("holiday :" +fields[0] + str(days))
                exception_file.write("DP," + fields[0] +",2\n")
                if ("SB" in days):
                    exception_file.write("SB," + fields[0] +",1\n")
                if("TS" in days):
                    exception_file.write("TS," + fields[0] +",1\n")  
                if("DS" in days):  
                    exception_file.write("DS," + fields[0] +",1\n")   
                    
        elif(weekday==5):
            if (not "SB" in days):
                print("holiday sunday:" + fields[0] + str(days))
                exception_file.write("DS," + fields[0] +",2\n")
                if("TS" in days):
                    exception_file.write("TS," + fields[0] +",1\n")
        
        
    return False     

def processKD(f,lines):
    print "Parsing section - KD - types of trips days"
    for line in f:
        if line[:1] == "#":
            break
    return False 

def processZA(f,lines):   
    print "Parsing section ZA stops groups" 
    for line in f:
        if line[:1] == "#":
            break
    return False 
    
def processZP(f,lines): 
    global wrong_stops,result_directory,debug_directory
    wrong_stops_file = open(debug_directory + '/wrong_stops.txt','w')
    stops_file = open(result_directory + '/stops.txt','w')
    stops_file.write("stop_id,stop_name,stop_lon,stop_lat\n")
    wrong_stops = dict()
    print "Parsing section ZA - stops"  
    nazwa = ''
    p = re.compile(".*Y= (\S*)\s*X= (\S*)")
    for line in f:
        
        if line[:1] == "#":
            break
        #print line[3:4]
        if line[3:4].isdigit():
            n = line[10:].split(',')
            if len(n) < 2:
                n=line[10:].split("--")
            nazwa = n[0]
            wstop = dict()
            lat = 0.0
            lon = 0.0
            i = 0
            f.next
            for line in f:
                if line[9:10].isdigit():
                    
                    
                    m = p.match(line[16:])
                    if m:
                        lat = lat + float(m.group(1))
                        lon = lon + float(m.group(2))
                        i = i+1
                        stops_file.write(line[9:15] + ',' + nazwa + " "+ line[13:15] + "," + m.group(1) + ',' + m.group(2) + "\n")
                    else:
                        wstop[line[9:15]] = line[9:]
                        #wrong_stops[line[9:15]] = line[9:]
                        #print "error:" + nazwa + " " + line[9:]    
                if line[6:7] == "#":
                    if i==0:
                        wrong_stops.update(wstop)
                        for key in wstop.keys():
                            wrong_stops_file.write(key+ ',' + nazwa + " "+ key[4:6] + ","  + ',' + "\n")
                        
                    else:
                        for key in wstop.keys():
                            stops_file.write(key+ ',' + nazwa + " "+ key[4:6] + ","  + str(lat/i) + ',' + str(lon/i) +"\n")
                            
                    break    
    print "wrong stops size " + str(len(wrong_stops)) 
    return False 

def processSM(f,lines):   
    print "Parsing section SM - places symbols"
    for line in f:
        if line[:1] == "#":
            break 
    return False 

def write_stop_times(tsfile, times_list, trip_id):
    i=1
    for tl in times_list:
        time = str(tl[1]).replace(".",":")
        tsfile.write(str(trip_id)+","+time+":00," +time+":00,"+tl[0] +","+str(i) +"\n")
        i = i+1
    
def processLL(f,lines):
    global result_directory,debug_directory,trips_file,stop_times_file,trips_id_dict
    print "Parsing section LL - routes and times " 
    routes_file = open(result_directory + '/routes.txt','w')
    stop_times_file = open(result_directory + '/stop_times.txt','w')
    trips_file = open(result_directory + '/trips.txt','w')
    routes_file.write("route_id,route_short_name,route_type\n")
    stop_times_file.write("trip_id,arrival_time,departure_time,stop_id,stop_sequence\n")
    trips_file.write("route_id,service_id,trip_id\n")
    counter = 0 
    infolinia = ""
    for line in f:
        if line[3:6] == "Lin":
            infolinia =  line.rstrip().split()
            print "Parsing line: " + line
            f.next
            #print l
            route_type = '3'
            l = infolinia[1]
            
            if  l[:2] == "KM" or l[:1]=="S" or l[:3] == "WKD":
                route_type='2'
            elif infolinia[1][:1].isdigit() and int(infolinia[1]) <100:
                route_type='0'
            
            routes_file.write(l + "," + l + "," + route_type + "\n")
                   
            processWK(f,infolinia[1])
        
            
        if counter > 10000000:
            break
        counter = counter+1
        if line[:1] == "#":
            break
    return False 

def processWK(f,numer_lini):
    global kursy_counter,dane_counter,trips, trips_sums, days , wrong_stops,trips_file,stop_times_file,trips_id_dict
    tsum_counter = len(trips_sums)
    for line in f:
        if line[6:9] == "*WK":
            #print line
            kursy = dict()
            przebieg_kursu = list()
            
            m = ''

            for line in f:
                
                if line[6:9] == "#WK":
                   
                    break
                
                pola = line.split()
                
                    
                    
  
                if(pola[0] in kursy):

                    m.update(pola[1])
                    przebieg_kursu.append([pola[1],pola[3]])
                else:
                    kursy_counter = kursy_counter+1
                    przebieg_kursu = list()
                    m = md5.new()
                    m.update(pola[1])
                    m.update(pola[2])
                    przebieg_kursu.append([pola[1],pola[3]])
                    kursy[pola[0]] = kursy_counter

                    
                        
                if len(pola)==5:
                    
                  
                    if (pola[4]=="P"):
                        if (m.digest() in trips_sums):
                            t = trips_sums[m.digest()] 
                            write_stop_times(stop_times_file, przebieg_kursu, t)
                               
                                
                        else:
                            # nalezy dodac nowy wpis do trips
                            tid =len(trips_sums)+1 
                            trips_file.write(numer_lini +"," + pola[2] + "," + str(tid) + "\n")
                            trips_sums[m.digest()] =  tid
                            
                            # zapisac rekordy w trip_tops
                            write_stop_times(stop_times_file, przebieg_kursu, tid)
                
                dane_counter=dane_counter+1  
              
            break    
           
    



def parse_file(directory,filename):
    global kursy_counter,dane_counter,sql_dane,sql_kursy,trips,trips_sums,days,result_directory,debug_directory
    trips = dict()
    trips_sums = dict()
    days = dict()
    result_directory = directory + '/target/' + filename
    debug_directory = directory + '/debug/'
    if not os.path.exists(result_directory):
        os.makedirs(result_directory) 
    else:
        print filename    
    shutil.copy (directory + "/template/agency.txt" , result_directory)    
    shutil.copy (directory + "/template/calendar.txt" , result_directory)    
    
    kursy_counter=1
    dane_counter=0
    f7z  = SevenZFile(directory +'/sync/' + filename + '.7z')

    retcode = False
    fo = f7z.readlines(filename +'.TXT')
    for line in fo:
        print line[1:3]
        if line[1:3] == "##":
            break
        retcode = eval('process' + line[1:3] +'(fo,' + line[4:]+')')
        if retcode:
            break
    
    
    with open(result_directory + "/stops.txt","a") as stopfile:      
        stopfile.write(open(directory + "/template/wrong_stops.txt").read())

         
        
        

