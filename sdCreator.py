#!/usr/bin/python

# Use for generating 'sd' entries for a vdBench parameters file.
# Relies on the system having SMdevices installed
# Written and tested against Python 2.6.6

vers = '0.5'

# TODO: 
#	* Get exception handling in getSMdevs() and getMpaths()
#	  working and on exception exit with a meaningful error msg 

import re, sys, subprocess, StringIO
from subprocess import Popen, PIPE
from optparse import OptionParser

# Build dictionary of /dev/sd paths and device info from SMdevices output for raw device I/O
# Only pulls preferred, in-use path(s) since this will either be a /dev/sd* or MPP managed /dev device
def getSMdevs():
	try:
	    sm_call = subprocess.Popen(["SMdevices"], shell=True, stdout=PIPE)
	except OSError as e:

	   	# This isn't working right at the moment but if SMdevices doesn't exist it throws a system error so.. /shrug

		print e
	
	sm_out = sm_call.communicate()[0]
	
	devs = dict()
	lnum = 1
	for line in StringIO.StringIO(sm_out):
		
		matchObj = re.match('\s{2}\/dev\/(sd\w{1,2})\s\(\S*\s\[Storage\sArray\s(\w*)\,\sVolume\s(\S*)\,\sLUN\s(\d{1,3})\,\sVolume\sID\s\<(\w*)\>\,\s(Preferred|Alternate)\sPath\s\(Controller\-([AB])\)\:\s(In\sUse|Owning)', line)
		if matchObj:
			devs[lnum] = {'sd': matchObj.group(1), 'sa': matchObj.group(2), 'volLbl': matchObj.group(3), 
					'lun': matchObj.group(4), 'volId': matchObj.group(5), 'path': matchObj.group(7)}
			lnum = lnum + 1

	return devs

# Build dictionary of mpath names and associated vol WWNs
# Only pulls those that are reported as LSI or NETAPP in VPD data
# -NOTE: there is a fourth match group in the regex for the INF-01-00 that is unused
def getMpaths():
	try:
	    m_call = subprocess.Popen((["multipath", "-ll"]), stdout=PIPE)
	except OSError as e:
		print e

	m_out = m_call.communicate()[0]
	
	mpathdevs = dict()
	en = 1
	for l in StringIO.StringIO(m_out):
		match_obj = re.match('(mpath\w+)\s\(\d{1}(\w+)\)\sdm\-\d+\s(LSI|NETAPP),(\w*-01-00)', l)
		if match_obj:
			if match_obj.group(3) in ('LSI','NETAPP'):
				mpathdevs[en] = {'name': match_obj.group(1), 'volId': match_obj.group(2)}
				en = en + 1
			else:
				continue
	return mpathdevs

# Generate the sd=. . . entries for use in a vdBench parameter file
# Takes an array name and bool for whether or not DMMP /dev/mapper paths
# should be returned instead of /dev/sd* paths with o_direct set.
def generateSdEntries(name, mp):
	print "\n"
        devTbl = getSMdevs()
	mpathTbl = getMpaths()
        index = 1

        for n in devTbl.keys():
       	        entryName = devTbl[n]['sa']
               	if name == entryName:
			if mp:
				for m in mpathTbl.keys():
					if devTbl[n]['volId'] == mpathTbl[m]['volId']:
						print "sd=sd" + str(index) + ",lun=/dev/mapper/" + mpathTbl[m]['name']
					else:
						continue
			else:
                       		print "sd=sd" + str(index) + ",lun=/dev/" + devTbl[n]['sd'] + ",openflags=o_direct"
                       	index = index + 1
               	else:
                       	continue

# Pretty print the getSMdevs() dictionary
def printDevs():
	
	d = getSMdevs()
	for l in d.keys():
		print " ", l, " /dev/" + d[l]['sd'], "\tSAName: " + d[l]['sa'], "\tVolume: " + d[l]['volLbl'], "\tLUN: " + d[l]['lun'], "\tVolID: " + d[l]['volId'], "\tPref Path: " + d[l]['path']
	print "\n"

# Run with menu driven interface
def run():

	print "\n"
	print "\t#########################################"
	print "\t####                                 ####"
	print "\t#### vdBench SD definition generator ####"
	print "\t####         for E-Series            ####"
	print "\t####             v", vers, "              ####"
	print "\t####                                 ####"
	print "\t#########################################"
	print "\n"

	while True:
		input = raw_input('\tSelect: (P)rint All, (G)enerate SD Definition, (Q)uit: ')
		
		if input.lower() not in ('p','g','q'):	
			print "\tInput was not recognized, please try again."
			continue
		else:
			if input.lower() == 'p':
				print "\n"
				printDevs()
				continue
			elif input.lower() == 'g':
				nmIn = raw_input('\tEnter SAName you want to create definitions for: ')
				mpaths = raw_input('\tDo you want DM-MP mpath devs? (Y/N): ')
				if mpaths.lower() == 'y':
					mpaths = 'True'
				else:
					mpaths = 'False'
				generateSdEntries(nmIn, mpaths)
				print "\n"
				continue
			elif input.lower() == 'q':
				print "\n"
				break
			else:
				continue		

# Run with command line arguments and no menu
def runWithArgs():

	parser = OptionParser()
	parser.add_option("-n", dest="saname", action="store", type="string", help="Storage array name to create sd definitions for")
	parser.add_option("-m", action="store_true", dest="mpath_d", default=False, help="Specify for DMMP /dev/mapper paths")

	(options, args) = parser.parse_args()

	if mpath_d == 'True':
		mp = 'y'
	else:
		mp ='n'

	generateSdEntries(saname, mp)
	sys.exit(0)

def main():
	
	if sys.argv[1:]:
		runWithArgs()
	else:
		run()	

if __name__ == "__main__":
	main()
	



	
