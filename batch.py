# status: functional but rudimentary
# next thing that needs to be done: write a proper output to file that displays data in a sensible format for plotting
	# against varied quantities
# currently only saves the data from the fort.* files; there are a number of other things being calculated in BURST, but
	# I'm not sure how to get them out of the Fortran results; talk to Evan about that once he finishes this round of
	# postdoc applications
# works for 3+1 models, not 3+2 models as yet

#!/usr/bin/python
import os
import time
from array import array
import json
import time
import datetime

# arrays for resultant quantities
# lists of lists of lists for concurrent mass/dilution variations

deuterium = []
#contained in fort.95
dneutronlifetime = []
ddilution = []
dhierarchy = []
dmass = []
deuterium.extend((dneutronlifetime, dhierarchy, ddilution, dmass))

helium = []
#contained in fort.94
hneutronlifetime = []
hhierarchy = []
hdilution = []
hmass = []
helium.extend((hneutronlifetime, hhierarchy, hdilution, hmass))

neff = []
#contained in fort.90
neffneutronlifetime = []
neffhierarchy = []
neffdilution = []
neffmass = []
neff.extend((neffneutronlifetime, neffhierarchy, neffdilution, neffmass))

#what is fort.91?  ~2.2e-2?

#these are global so I can write them out to a file
global minneutronlifetime, deltaneutronlifetime, status, mindilution, maxdilution, deltadilution, dminmass
global dmaxmass, ddeltamass, maxmass, minmass, deltamass, nuclearlifetime, hierarchy, modifysteriles, n, l, inner

#in lists, bin 0 contains data from modified neutron lifetime, bin 1 contains data for both normal (1,0) and inverted (1,1)
	#hierarchies, bin 2 contains linked lists for mass/dilution factors

delta = raw_input("Do you want to change parameters?  Y/N: ")
if (str(delta) == "Y"):

	# change neutron lifetime
	# this assumes that the value the code should be returned to after running is 885.7; I think this is reasonable for the moment.
	nuclearlifetime = raw_input("Do you want to change neutron mean lifetime?  Y/N: ")
	if (str(nuclearlifetime) == "Y" or str(nuclearlifetime) == "y"):
		
		minneutronlifetime = raw_input("What is the minimum nuclear lifetime you want to use? ")
		deltaneutronlifetime = raw_input("What is the change in nuclear lifetime you want per run? ")
		maxneutronlifetime = raw_input("What is the maximum nuclear lifetime you want to use? ")
		
		# this is a horrible, horrible kludge, because for some reason, <= will always return false
		# it works fine on other variables!  but not here!  WHY?  I HAVE NO IDEA.
		maxneutronlifetime = float(maxneutronlifetime) + 0.00000001
		
		# read in initial conditions
		f = open('bbn_params.ini','r')
		filedata = f.read()
		f.close()
		
		starting = 885.7
		neutronlifetime = float(minneutronlifetime)
		
		newdata = filedata
		
		while (float(maxneutronlifetime) > float(neutronlifetime)):
			print "running neutron lifetime = " + str(neutronlifetime)
			
			# replace initial condition with the new value
			newdata = newdata.replace(str(starting),str(neutronlifetime))
	
			# reopen file, overwrite it with new value
			f = open('bbn_params.ini','w')
			f.write(newdata)
			f.close()
			
			# run code
			os.system("make clean; make depend; make")
			os.system("./burst")
			
			# copy deuterium abundance
			f2 = open('fort.95', 'r')
			currdeu = float(f2.read())
			f2.close()
			deuterium[0].append(currdeu)
			# print deuterium[0]
			
			# copy helium abundance
			f2 = open('fort.94', 'r')
			currhelium = float(f2.read())
			f2.close()
			helium[0].append(currhelium)
			# print helium[0]
			
			# copy neff
			f2 = open('fort.90', 'r')
			currneff = float(f2.read())
			f2.close()
			neff[0].append(currneff)
			# print neff[0]
			
			starting = neutronlifetime
			neutronlifetime = float(neutronlifetime) + float(deltaneutronlifetime)
						
		#change data file back to initial state, so that using this batch script does not affect future runs
		f = open('bbn_params.ini', 'w')
		f.write(filedata)
		f.close()
		
	hierarchy = raw_input("Do you want to run with both hierarchies (normal, inverted)?  Y/N: ")
	if (str(hierarchy) == "Y" or str(hierarchy) == "y"):
		
		# read in initial conditions
		f = open('recom_params.ini','r')
		filedata = f.read()
		f.close()
		
		#run with initial conditions
		os.system("make clean; make depend; make")
		os.system("./burst")
		
		# copy deuterium abundance
		f2 = open('fort.95', 'r')
		currdeu = float(f2.read())
		f2.close()
		deuterium[1].append(currdeu)
			
		# copy helium abundance
		f2 = open('fort.94', 'r')
		currhelium = float(f2.read())
		f2.close()
		helium[1].append(currhelium)
			
		# copy neff
		f2 = open('fort.90', 'r')
		currneff = float(f2.read())
		f2.close()
		neff[1].append(currneff)
		
		# determine initial condition
		loc = filedata.find("! = hierflag")
		start = loc - 6
		end=start+4
		status = filedata[start:end]
		
		#switch hierarchy flag
		if (status == "true"):
			newdata = filedata.replace(".true. ! = hierflag", ".false. ! = hierflag")
		else:
			newdata = filedata.replace(".false. ! = hierflag", ".true. ! = hierflag")
		
		# write out new version
		f = open('recom_params.ini','w')
		f.write(newdata)
		f.close()
			
		#run again
		os.system("make clean; make depend; make")
		os.system("./burst")
		
		# copy deuterium abundance
		f2 = open('fort.95', 'r')
		currdeu = float(f2.read())
		f2.close()
		deuterium[1].append(currdeu)
			
		# copy helium abundance
		f2 = open('fort.94', 'r')
		currhelium = float(f2.read())
		f2.close()
		helium[1].append(currhelium)
			
		# copy neff
		f2 = open('fort.90', 'r')
		currneff = float(f2.read())
		f2.close()
		neff[1].append(currneff)
		
		# return to original state
		f = open('recom_params.ini', 'w')
		f.write(filedata)
		f.close()
		
	# now the important bit: changing the sterile neutrino parameters
	deuteriumdilutiononly = []
	deuteriummass = []
	deuterium[2].extend((deuteriumdilutiononly, deuteriummass))
	
	heliumdilutiononly = []
	heliummass = []
	helium[2].extend((heliumdilutiononly, heliummass))
	
	neffdilutiononly = []
	neffmass = []
	neff[2].extend((neffdilutiononly, neffmass))
	
	modifysteriles = raw_input("Do you want to change the dilution of the sterile species?  Y/N: ")
	if (str(modifysteriles) == "Y" or str(modifysteriles) == "y"):
		mindilution = raw_input("What is the lowest dilution factor you wish to use?  ")
		deltadilution = raw_input("How much do you want to change the dilution factor per run?  ")
		maxdilution = raw_input("What is the maximum dilution factor you wish to use?  ")
		
		# why do some of these <= loops work properly when others don't?  I HAVE NO IDEA.
		maxdilution = float(maxdilution) + float(0.00000001)
			
		# read in initial parameters
		f = open('main_params.ini','r')
		filedata = f.read()
		f.close()
			
		#add a sterile species if not already defined
		start = filedata.find("! = nnu (number of neutrinos, must be >= 3)") - 2
		end = start + 1
		nnu = filedata[start:end]
		
		#I have to define this out here or I can't use it outside the if statement
		newfile = ""
		
		if (float(nnu) == 3):
			newfile = filedata.replace("3 ! = nnu (number of neutrinos, must be >= 3)", "4 ! = nnu (number of neutrinos, must be >= 3)")
		elif (float(nnu) == 5):
			newfile = filedata.replace("5 ! = nnu (number of neutrinos, must be >= 3)", "4 ! = nnu (number of neutrinos, must be >= 3)")
		else:
			newfile = filedata
			
		f = open('main_params.ini', 'w')
		f.write(newfile)
		f.close()
		
		currdilution = float(mindilution)
		index1 = 0
			
		starting = "1.0d0 ! = stdil (dilution temperature of sterile nu)"
		
		# and now the reason for the nested lists
		alsomodifymass = raw_input("Do you want to modify the sterile neutrino mass as well?  Y/N: ")
		
		setmass = "false"
		dminmass = 0
		dmaxmass = 0
		ddeltamass = 0
		n = 0
		l = 0
		
		while (float(currdilution) <= float(maxdilution)):
			newdilution = str(currdilution) + "d0 ! = stdil (dilution temperature of sterile nu)"
					
			#replace dilution factor
			loc = newfile.find(starting)
			newfile = newfile.replace(starting, newdilution)

			#write out to file			
			f = open('main_params.ini','w')
			f.write(newfile)
			f.close()
					
			if (str(alsomodifymass) == "Y" or str(alsomodifymass) == "y"):
				if (setmass == "false"):
					dminmass = raw_input("What is the minimum sterile neutrino mass you wish to test? ")
					# I'm pretty sure that the code expects a mass in eV, but I should confirm that.
					ddeltamass = raw_input("How much do you want the sterile neutrino mass to change each run? ")
					dmaxmass = raw_input("What is the maximum sterile neutrino mass you wish to test? ")
					dmaxmass = float(dmaxmass) + float(0.0000001)
					setmass = "true"
					
				currmass = float(dminmass)
					
				starting2 = "1.0d0 ! = stmass (sterile nu mass)"
					
				while (float(currmass) <= float(dmaxmass)):
					newmass = str(currmass) + "d0 ! = stmass (sterile nu mass)"
					
					#replace dilution factor
					loc2 = newfile.find(starting2)
						
					# continue editing with mass value
					newfile = newfile.replace(starting2, newmass)
						
					#write out to file			
					f = open('main_params.ini','w')
					f.write(newfile)
					f.close()
						
					os.system("make clean; make depend; make")
					os.system("./burst")
						
					# copy deuterium abundance
					f2 = open('fort.95', 'r')
					currdeu = float(f2.read())
					f2.close()
					(deuterium[2])[1].append(currdeu)
						
					# copy helium abundance
					f2 = open('fort.94', 'r')
					currhelium = float(f2.read())
					f2.close()
					(helium[2])[1].append(currhelium)
			
					# copy neff
					f2 = open('fort.90', 'r')
					currneff = float(f2.read())
					f2.close()
					(neff[2])[1].append(currneff)
						
					print "deuterium abundance: " + str(currdeu)
					print "helium abundance: " + str(currhelium)
					print "neff: " + str(currneff)
						
					starting2 = newmass
					currmass = currmass + float(ddeltamass)
					n = n+1
						
				# return to original state
				f = open('main_params.ini', 'w')
				f.write(filedata)
				f.close()
				
				currmass = dminmass
			else:
				os.system("make clean; make depend; make")
				os.system("./burst")
					
				# copy deuterium abundance
				f2 = open('fort.95', 'r')
				currdeu = float(f2.read())
				f2.close()
				(deuterium[2])[0].append(currdeu)
			
				# copy helium abundance
				f2 = open('fort.94', 'r')
				currhelium = float(f2.read())
				f2.close()
				(helium[2])[0].append(currhelium)
			
				# copy neff
				f2 = open('fort.90', 'r')
				currneff = float(f2.read())
				f2.close()
				(neff[2])[0].append(currneff)
				
			index1 = index1 + 1
			starting = newdilution
			currdilution = currdilution + float(deltadilution)
			l = l+1
		
		# return to original state
		f = open('main_params.ini', 'w')
		f.write(filedata)
		f.close()
		
	mass = raw_input("Do you want to change the sterile neutrino mass (without changing the dilution factor)?  Y/N: ")
	if (str(mass) == "Y" or str(mass) == "y"):
		
		minmass = raw_input("What is the sterile mass you want to use? ")
		deltamass = raw_input("What is the change in mass you want per run? ")
		maxmass = raw_input("What is the maximum mass you want to use? ")
		
		# read in initial conditions
		f = open('main_params.ini','r')
		filedata = f.read()
		f.close()
		
		currmass = float(minmass)
		
		starting = 1.0
		
		newdata = filedata
		
		while (currmass <= float(maxmass)):
			print "running mass = " + str(currmass)
			
			# replace initial condition with the new value
			newdata = newdata.replace(str(starting) + "d0 ! = stmass (sterile nu mass)", str(currmass) + "d0 ! = stmass (sterile nu mass)")

			# reopen file, overwrite it with new value
			f = open('main_params.ini','w')
			f.write(newdata)
			f.close()
			
			# run code
			os.system("make clean; make depend; make")
			os.system("./burst")
			
			# copy deuterium abundance
			f2 = open('fort.95', 'r')
			currdeu = float(f2.read())
			f2.close()
			deuterium[3].append(currdeu)
			
			# copy helium abundance
			f2 = open('fort.94', 'r')
			currhelium = float(f2.read())
			f2.close()
			helium[3].append(currhelium)
			
			# copy neff
			f2 = open('fort.90', 'r')
			currneff = float(f2.read())
			f2.close()
			neff[3].append(currneff)
			
			print "deuterium abundance: " + str(currdeu)
			print "helium abundance: " + str(currhelium)
			print "neff: " + str(currneff)
			
			starting = currmass
			currmass = float(currmass) + float(deltamass)
		
		#change data file back to initial state, so that using this batch script does not affect future runs
		f = open('main_params.ini', 'w')
		f.write(filedata)
		f.close()
	
	g = open('output.txt', 'w')
	output = "Run at " + str(time.asctime(time.localtime(time.time()))) + "\n\n"
	
	if ((nuclearlifetime == "Y") or (nuclearlifetime == "y")):
		output = output + "Nuclear Lifetime	Deuterium		Helium		Neff"
		for x in range(0, len(deuterium[0])):
			currvalue = float(minneutronlifetime) + float(x)*float(deltaneutronlifetime)
			output = output + "\n" + str(currvalue) + "			" + str((deuterium[0])[x]) + "	" \
				+ str((helium[0])[x]) + "	" + str((neff[0])[x])
		output = output + "\n\n"
	
	if ((hierarchy == "Y") or (hierarchy == "y")):
		output = output + "Hierarchy	Deuterium		Helium		Neff"
		if (status == "true"):
			output = output + "\n" + "Normal" + "		" + str((deuterium[1])[0]) + "	" \
				 + str((helium[1])[0]) + "	" + str((neff[1])[0]) + "\n" + "Inverted"  + "	" \
				 + str((deuterium[1])[1]) + "	" + str((helium[1])[1]) + "	" + str((neff[1])[1])
		else:
			output = output + "\n" + "Inverted" + "	" + str((deuterium[1])[0]) + "	" + str((helium[1])[0]) \
				+ "	" + str((neff[1])[0]) + "\n" + "Normal"  + "		" + str((deuterium[1])[1]) + "	" \
				+ str((helium[1])[1]) + "	" + str((neff[1])[1])
		
		output = output + "\n\n"	
	
	if ((modifysteriles == "Y") or (modifysteriles == "y")):
		if ((alsomodifymass == "Y") or (alsomodifymass == "y")):
			output = output + "Dilution Factor		Sterile Mass	Deuterium		Helium		Neff"
			for x in range(0, l):
			
				currdilution = float(mindilution) + float(x)*float(deltadilution)
				
				for y in range(0, inner):
					currmass = float(dminmass) + float(y)*float(ddeltamass)
					output = output + "\n" + str(currdilution) + "			" + str(currmass) + "		" \
						+ str(((deuterium[2])[1])[n-1]) + "	" + str(((helium[2])[1])[n-1]) + "	"
					output = output + str(((neff[2])[1])[n-1])
		else:
			output = output + "Dilution Factor		Deuterium		Helium		Neff"
			for x in range(0, len((deuterium[2])[0])):
				currvalue = float(mindilution) + float(x)*float(deltadilution)
				output = output + "\n" + str(currvalue) + "			" + str(((deuterium[2])[0])[x]) + "	" \
				 	+ str(((helium[2])[0])[x]) + "	" + str(((neff[2])[0])[x])
			
			output = output + "\n\n"
		
	if ((mass == "Y") or (mass == "y")):
		output = output + "Sterile neutrino mass	Deuterium		Helium		Neff"
		for x in range(0, len(deuterium[3])):
			currvalue = float(minmass) + float(x)*float(deltamass)
			output = output + "\n" + str(currvalue) + "			" + str((deuterium[3])[x]) + "	" \
				 + str((helium[3])[x]) + "	" + str((neff[3])[x])
		output = output + "\n\n"	
	
	g.write(output)