#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import sys, re, datetime
	
def usage() :
	print "Usage : "
	print sys.argv[0] + " <file.pdf>"
	exit()

#fonction permettant de rendre lisible les données de date
def readableDate(raw_dateString) :
	year = int(raw_dateString[:4])
	mouth = int(raw_dateString[4:6])
	day = int(raw_dateString[6:8])
	hour = int(raw_dateString[8:10])
	minute = int(raw_dateString[10:12])
	second = int(raw_dateString[12:14])
	GMT = raw_dateString[14:-1]
	
	return (str(datetime.datetime(year, mouth, day, hour, minute, second)) + " GMT " + GMT)

#verification des arguments 
if len(sys.argv) < 2 or sys.argv[1] == "-h" :
	usage()	

#ouverture du fichier donner par l'utilisateur
try :
	fd = open(sys.argv[1], 'r')
except : 
	print "fichier non valide"
	print "" 
	usage()
	exit()
	
data = fd.read()

#verification que le fichier est bien un fichier PDF
if data[:4] != "%PDF" : 
	print "le fichier n'est pas un PDF"
	print ""
	usage()
	exit()

#recherche du champ indiquant l'emplacement de la zone d'info
groups = re.search(r'/Info \d{1,3} \d{1} R', data)

#split par "endobj" et recherche de la zone avec nos infos
for raw_meta in data.split("endobj") :
	if groups.group(0).split(" ", 1)[1].replace('R', 'obj') in raw_meta :
		buf_meta = raw_meta.split("<<")
		
#si la variable 'buf_meta' n'existe pas, elle n'est pas initialisé, donc on a pas trouvé les meta. 
if 'buf_meta' not in locals():
	print "no metadata"
	exit()

tab_values_raw = []

buf = ""
first = True
# on repere chaque champs 
for x in re.split('(/[A-Z])', buf_meta[1]) :
	if x != '' :
		if x[0] in "/" :
			# pour ne as déclancher a la premiere occurence
			if first == False :
				tab_values_raw.append(buf[1:].replace('\n', ''))
			first = False
			buf = x	
		else :
			buf += x
tab_values_raw.append(buf[1:].replace('\n', '').replace('>>', ''))

for meta in tab_values_raw : 

	#si on a un '<', nous devons lire une hexstring
	if '<' in meta : 
		name = meta.split('<')[0]
		value_raw = meta.split('<')[1][:-1]

		if value_raw[:4] == "FEFF" :
			#on doit prendre 2 caractere sur 2 XX..XX..XX..XX
			buf_value = ['0x'+value_raw[meta:meta+2] for meta in range(0, len(value_raw), 2)][3:]
		
			#on transforme en int puis on join la liste pour avoir une chaine de caractere
			value = "".join([chr(int(buf_value[y], 16)) for y in range(0, len(buf_value), 2)])

		print name + " : " + value
	else :

		#si on trouve la string "D:", nous avons une information de date
		if re.search("D:", meta) :
			dateString = readableDate(meta.split("D:")[1].replace(")", ''))

			print meta.split("D:")[0].replace("(", '') + " : " + dateString
		else :
			line = " ".join(meta.replace("\\", '').split("(")).replace(")", '').split(" ")
			print line[0] + " : " + " ".join(line[1:])
