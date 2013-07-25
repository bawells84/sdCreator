#!/usr/bin/python

import re,sys,subprocess
from optparse import OptionParser

def sdExtract():
	try:
	    out = Popen(["SMdevices"]).communicate()
	except Exception as e:
	    print "SMdevices failed with returncode:", e, "\n"
	    print "Output:\n"
	
	devs = dict()
	lnum = 1
	for line in out:
		matchObj = re.match(r'\s{2}\/dev\/(sd\w{1,2})\s\(\S*\s\[Storage\sArray\s(\w*)\,\sVolume\s(\S*)\,\sLUN\s(\d{1,3})\,\sVolume\sID\s\<(\w*)\>\,\s(Preferred|Alternate)\sPath\s\(Controller\-([AB])\)\:\s(In\sUse|Owning)', line, re.M)
		if matchObj:
			devs[lnum] = {'sd': matchObj.group(1), 'sa': matchObj.group(2), 'volLbl': matchObj.group(3), 
				      'lun': matchObj.group(4), 'volId': matchObj.group(5), 'path': matchObj.group(7)}
			lnum = lnum + 1

	return devs

def drawDevTable(d):
	
	print " Ln  /dev       StorageArray		 Volume			          LUN  Volume WWID			     Preferred Path\n"
	print "+---+----------+-------------------------+--------------------------------+----+-------------------------------------+--------------\n"
	for l in devs.iteritems():
		print " ", l, " /dev/sd", devs[l]['sd'], " ", devs[l]['sa'], "	", devs[l]['volLbl'], "\t", devs[l]['lun'], " ", devs[l]['volId'], "\t", devs[l]['path'], "\n"  
		  	
		

def main():
	d = sdExtract()
	drawDevTable(d)

if __name__ == "__main__":
	main()
	



	
