# GTFS4ZTM_waw
Python script for creating GTFS (General Transit Feed Specification) from ZTM (http://www.ztm.waw.pl) publicly available schedules

Scripts works in current directory, connects to ZTM FTP server, fetches latest schedules and creates GTFS files in 'target/<schedule filename>/' subdirectory. 

Schedules are publicly available - terms and conditions are here (in Polish):
http://www.ztm.waw.pl/?c=628&l=1

General remarks:
- WKD and KM are owned by different entities - and onlhy partial schedules are available (not all stations)
- No schedule for Metro lines (M1 and M2)
- debug/wrong_stops.txt lists stops for which ZTM doesn't publish coordinates
