#!/usr/bin/python

# Use for generating 'sd' entries for a vdBench parameters file.
# This right now this only works with /dev/sd* devices and as such only works returns in-use pathing
# adding logic to handle reconiling to mpath devs for DMMP is on the to-do
# Relies on the system having SMdevices installed
# Written and tested against Python 2.6.6

import re, sys, subprocess, StringIO
from subprocess import Popen, PIPE
from optparse import OptionParser

def sdExtract():
	try:
	    call = subprocess.Popen(["SMdevices"], shell=True, stdout=PIPE)
	except OSError as e:

	   	# This isn't working right at the moment but if SMdevices doesn't exist it throws a system error so.. /shrug

		print e
	
	out = call.communicate()[0]
	
	devs = dict()
	lnum = 1
	for line in StringIO.StringIO(out):
		
		matchObj = re.match('\s{2}\/dev\/(sd\w{1,2})\s\(\S*\s\[Storage\sArray\s(\w*)\,\sVolume\s(\S*)\,\sLUN\s(\d{1,3})\,\sVolume\sID\s\<(\w*)\>\,\s(Preferred|Alternate)\sPath\s\(Controller\-([AB])\)\:\s(In\sUse|Owning)', line)
		if matchObj:
			devs[lnum] = {'sd': matchObj.group(1), 'sa': matchObj.group(2), 'volLbl': matchObj.group(3), 
					'lun': matchObj.group(4), 'volId': matchObj.group(5), 'path': matchObj.group(7)}
			lnum = lnum + 1

	return devs

def drawDevTable(d):
	
	for l in d.keys():
		print " ", l, " /dev/" + d[l]['sd'], "\tSAName: " + d[l]['sa'], "\tVolume: " + d[l]['volLbl'], "\tLUN: " + d[l]['lun'], "\tVolID: " + d[l]['volId'], "\tPref Path: " + d[l]['path']

def generateSdEntries(name):
	print "\n"
        devTbl = sdExtract()
        index = 1
        for n in devTbl.keys():
                entryName = devTbl[n]['sa']
                if name == entryName:
                        print "sd=sd" + str(index) + ",lun=/dev/" + devTbl[n]['sd'] + ",openflags=o_direct"
                        index = index + 1
                else:
                        continue

def getDevs():
	
	d = sdExtract()
	drawDevTable(d)
	print "\n"
	
def main():
	
	print "\n"
	print "\t#########################################"
	print "\t####                                 ####"
	print "\t#### vdBench SD definition generator ####"
	print "\t####         for E-Series            ####"
	print "\t####             v 0.1               ####"
	print "\t####                                 ####"
	print "\t#########################################"
	print "\n"
	
	while True:
		input = raw_input('\tSelect: (P)rint All, (G)enerate SD Definition, (Q)uit: ')
		
	#	if str.isalpha(input) == 'False':
		if input.lower() not in ('p','g','q'):	
			print "\tInput was not recognized, please try again."
			continue
		else:
			if input.lower() == 'p':
				print "\n"
				getDevs()
				continue
			elif input.lower() == 'g':
				nmIn = raw_input('\tEnter SAName you want to create definitions for: ')
				generateSdEntries(nmIn)
				print "\n"
				continue
			elif input.lower() == 'q':
				print "\n"
				break
			else:
				continue		

if __name__ == "__main__":
	main()
	



	
