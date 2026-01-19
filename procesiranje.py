from pprint import pprint
from datetime import datetime,timedelta
import numpy
import matplotlib.pyplot as plt
import matplotlib.cm as cm 
from mpl_toolkits.mplot3d import Axes3D
import scipy.interpolate
import glob, os
import matplotlib.colors as colors
from matplotlib.colors import LinearSegmentedColormap
import shutil
import os, re, os.path

"""
Author: Miha Smrekar

Ta modul je namenjen procesiranju podatkov meritev, opravljenih s pomocjo traverznega sistema,
in anemometra, ki shranjuje podatke v XLS datoteko.

Casovno oznaceni podatki o lokaciji traverze so shranjeni v datotekah casi_[datum in cas zacetka meritve].
Casovno oznaceni podatki merjenja so shranjeni v AHB01000.XLS, AHB01002.XLS, itd.
"""


def calculate_averages(pdict):
	"""
	Za izdelavo output seznama tock z povprecnimi hitrostmi in ostalimi podrobnostmi
	"""
	output_list = []
	all_temps = []
	all_speeds = []
	for k,v in pdict.items():
		x,y,z = k
		list_speeds = []
		list_temps = []
		for m in v["measurements"]:
			speed,unit_speed,temp,unit_temp,date = m
			list_speeds.append(speed)
			list_temps.append(temp)
			all_temps.append(temp)
			all_speeds.append(speed)
		avg_speed = numpy.average(list_speeds)
		avg_temp = numpy.average(list_temps)
		std_dev_speed = numpy.std(list_speeds)
		std_dev_temp = numpy.std(list_temps)
		turbulence = 100.0*std_dev_speed/avg_speed
		output_list.append({
							"x":x,
							"y":y,
							"z":z,
							"avg_speed":avg_speed,
							"avg_temp":avg_temp,
							"std_dev_speed":std_dev_speed,
							"std_dev_temp":std_dev_temp,
							"turbulence":turbulence
							})
	global_speed = numpy.average(all_speeds)
	global_temp = numpy.average(all_temps)
	global_speed_std = numpy.std(all_speeds)
	global_temp_std = numpy.std(all_temps)
	return {"output_list":output_list,
			"global_speed":global_speed,
			"global_temp":global_temp,
			"global_speed_std":global_speed_std,
			"global_temp_std":global_temp_std
			}


def izrisi_tocke(points_dict,traverse_locations,MAPA_MERITVE,prikazi=False,shrani=True):
	list_points = calculate_averages(points_dict)
	# Vzami primerne x,y,z tocke za graf.
	#     Ker je 0,0 traverze v resnici 1000,1000, damo spredaj minus, da zgleda graf pravilno.
	
	x = [-l["y"] for l in list_points["output_list"]]
	y = [-l["z"] for l in list_points["output_list"]]
	
	for i in ["avg_speed","avg_temp","std_dev_speed","std_dev_temp","turbulence"]:
		z = [l[i] for l in list_points["output_list"]]

		if i == "avg_speed":
			predpona = 'Povprecna_hitrost_'
			unit = 'm/s'
		elif i == "avg_temp":
			predpona = 'Povprecna_temperatura_'
			unit = '°C'
		elif i == "std_dev_speed":
			predpona = 'Standardni_odklon_hitrost_'
			unit = 'm/s'
		elif i == "std_dev_temp":
			predpona = 'Standardni_odklon_temperatura_'
			unit = '°C'
		elif i == "turbulence":
			predpona = "Stopnja_turbulence_"
			unit = '%'

		draw_to_matplotlib(
			x=x,
			y=y,
			z=z,
			traverse_locations=traverse_locations,
			MAPA_MERITVE=MAPA_MERITVE,
			predpona=predpona,
			prikazi=prikazi,
			shrani=shrani,
			save_folder='slikice',
			unit=unit)
		if i=="avg_speed":
			draw_to_matplotlib(
				x=x,
				y=y,
				z=z,
				traverse_locations=traverse_locations,
				MAPA_MERITVE=MAPA_MERITVE,
				predpona=predpona,
				prikazi=prikazi,
				shrani=shrani,
				save_folder='slikice_absolute',
				absolute_scale=True,
				absolute_min=0,
				absolute_max=30,
				unit=unit)


def draw_to_matplotlib(x,y,z,traverse_locations,MAPA_MERITVE,predpona,prikazi,shrani,save_folder,absolute_scale=False,absolute_min=0,absolute_max=30,unit=''):
	# Ne vem ali je to potrebno. Menda je.
	x = numpy.array(x)
	y = numpy.array(y)
	z = numpy.array(z)

	# x/y tocke za risati ozadje
	xi, yi = numpy.linspace(x.min(), x.max(), 100), numpy.linspace(y.min(), y.max(), 100)
	xi, yi = numpy.meshgrid(xi, yi)

	# Linearna interpolacija ozadja, glede na x,y,z
	rbf = scipy.interpolate.Rbf(x, y, z, function='cubic')
	zi = rbf(xi, yi)


	plt.imshow(zi, vmin=z.min(), vmax=z.max(), origin='lower',
		        extent=[x.min(), x.max(), y.min(), y.max()], cmap=cm.jet)
	if absolute_scale:
		plt.clim(absolute_min,absolute_max) #absolutne vrednosti colormapa

	plt.xlim(-1000,0)
	plt.ylim(-1000,0)

	plt.xlabel('Min:%.2f Max:%.2f Avg:%.2f' % (z.min(),z.max(),numpy.mean(z)))
	
	plt.scatter(x, y, c=z, cmap=cm.jet)
	if absolute_scale:
		plt.clim(absolute_min,absolute_max) #absolutne vrednosti colormapa
	


	cbar = plt.colorbar()
	cbar.ax.set_xlabel(unit)
	folder_name, file_name = os.path.split(traverse_locations)
	plt.title(predpona+file_name)
	if prikazi:
		plt.show()
	if shrani:
		samo_odstotki = file_name.split('_')[-1]
		filename = "%s.png" % (predpona+samo_odstotki)

		path = os.path.join(MAPA_MERITVE,save_folder,filename)
		#print(path)
		plt.savefig(path)
		plt.clf()


def seznam_tock(traverse_locations):
	"""
	Funkcija prejme ime datoteke, ki ima notri spravljene case premikov in ustavitev traverze.

	Vrne pa knjiznico tock brez meritev.
	"""

	print(traverse_locations)

	# Odpri datoteko od seznama lokacij
	f_locations = open(traverse_locations,"r")

	# Vrstice v seznam
	lines = f_locations.readlines()

	# Zapri datoteko
	f_locations.close()

	# Shramba za točke
	points_dict = {}

	# Shrani točke v shrambo
	i=0
	for l in lines:
		if "mov_start" in l:
			tip,day,date = l.split(",")
			date= date.strip()
			date_obj = datetime.strptime(date,'%d %b %Y %H:%M:%S')
			if i != 0:
				#za prejsnjo tocko point_start napisi da se je koncala ob (tem) mov_start
				points_dict[dict_tuple]["end_point"] = date_obj
		elif "point_start" in l:
			tip,day,date,x,y,z = l.split(",")
			x,y,z = float(x),float(y),float(z)
			dict_tuple = (x,y,z)
			date = date.strip()
			date_obj = datetime.strptime(date,'%d %b %Y %H:%M:%S')
			points_dict[dict_tuple] = {"srt_point":date_obj,"measurements":[]}
		elif "point_end" in l:
			tip,day,date,x,y,z = l.split(",")
			x,y,z = float(x),float(y),float(z)
			dict_tuple = (x,y,z)
			date = date.strip()
			date_obj = datetime.strptime(date,'%d %b %Y %H:%M:%S')
			points_dict[dict_tuple]["end_point"] = date_obj
		i+=1

	return points_dict

	


def get_point_from_time(points_dict):
	"""
	Funkcija prejme knjiznico tock.

	Vrne pa funkcijo, s pomocjo katere lahko:
		-vstavis cas (datetime object),
		-dobis tocko v obliki tuple-a (x,y,z), ce je traverza v tistem trenutku mirovala,
			sicer None.
	"""

	# Zgeneriraj back-search seznam, s pomocjo katerega potem searchamo kateri tocki pripada cas

	start_times = []
	end_times = []
	#print(points_dict)

	for k,v in points_dict.items():
		#print(v)
		start = v["srt_point"]
		start_times.append((start,k))
		end = v["end_point"]
		end_times.append((end,k))

	sorted(start_times)
	sorted(end_times)

	def search(datetime_obj):
		i=0
		for t in start_times:
			if datetime_obj > start_times[i][0] and datetime_obj < end_times[i][0]:
				return start_times[i][1]
			i=i+1
		return None
	return search


def tockam_dodaj_meritve(points_dict,MAPA_MERITVE):
	"""
	Funkcija prejme knjiznico tock, ki nimajo dodanih meritev in funkcijo, ki ti za dani cas vrne pozicijo koordinatke.
	Vrne dopolnjeno knjiznico tock z meritvami.
	"""


	# Odpri datoteko od anemometra
	all_lines = []

	for xls_meritve in glob.glob(os.path.join(MAPA_MERITVE,"AHB*.XLS")):
		#print(xls_meritve)
		f_measurements = open(xls_meritve)
		lines = f_measurements.readlines()
		all_lines += lines


	get_location = get_point_from_time(points_dict)

	# Shrani vse izmerjene merilne tocke v shrambo tock
	i=0
	for l in all_lines:
		if not "Date" in l and not "Time" in l:
			place,date,time,value_speed,unit_speed,value_temp,unit_temp = l.split("\t")
			value_speed = value_speed.replace('"',"")
			value_speed = value_speed.replace(",",".")
			value_temp = value_temp.replace('"',"")
			value_temp = value_temp.replace(",",".")
			date_time = date+" "+time
			try:
				#ocitno je mozno da naprava shranjuje v obeh formatih, kakor ji sede
				date_obj = datetime.strptime(date_time,'%Y/%m/%d %H:%M:%S')
			except ValueError:
				date_obj = datetime.strptime(date_time,'%m/%d/%Y %H:%M:%S')
			
			a = get_location(date_obj)
			if a != None:
				points_dict[a]["measurements"].append((float(value_speed),unit_speed,float(value_temp),unit_temp,date_obj))
	return points_dict


def correlate_data(traverse_locations,MAPA_MERITVE):
	"""
	Funkcija prejme ime datoteke, ki vsebuje lokacije traverze.

	Nato sama najde in sprocesira vse AHB0*.XLS datoteke in
	vrne dictionary z meritvami za vsako lokacijo.

	Primer izhoda:

		{(0, 0, 0): {'end_point': datetime.datetime(2019, 1, 25, 11, 40, 3),
	             	 'measurements': [(16.7,
	                               	  'm/S     ',
	                                  12.5,
	                                  'AMTemp C\n',
	                                  datetime.datetime(2019, 1, 25, 11, 39, 54)),
	                 'srt_point': datetime.datetime(2019, 1, 25, 11, 39, 53)}}

	(0,0,0) je primarni kljuc knjiznice. Oznacuje x,y,z lokacijo traverze.
	Primarna vrednost knjiznice je nova knjiznica.
	Nova knjiznica vsebuje naslednje kljuce in vrednosti:
		'srt_point' : vsebuje datetime object, ki oznacuje prvi trenutek, ko je traverza prispela na dano lokacijo.
		'end_point' : vsebuje datetime object, ki oznacuje trenutek, ko se je traverza zacela premikati na drugo lokacijo.
		'measurements' : pa je seznam tupleov, ki vsebujejo:
			[(float) hitrost vetra, (str) enota, (float) temperaturo, (str) enoto, (datetime obj) cas meritve]
	"""

	points_dict = seznam_tock(traverse_locations)

	points_dict = tockam_dodaj_meritve(points_dict,MAPA_MERITVE)

	return points_dict



def izris(MAPA_MERITVE):
	for file in glob.glob(os.path.join(MAPA_MERITVE,"casi_*")):
	    correlated_data = correlate_data(file,MAPA_MERITVE)
	    izrisi_tocke(correlated_data,file,MAPA_MERITVE)

def get_data(MAPA_MERITVE):
	out_list = []
	for file in glob.glob(os.path.join(MAPA_MERITVE,"casi_*")):
	    correlated_data = correlate_data(file,MAPA_MERITVE)
	    head, tail = os.path.split(file)
	    percent = tail.split('_')[-1]
	    percent_num = percent.split('p')[0]
	    #print(correlated_data)
	    for loc, d in correlated_data.items():
	    	for m in d['measurements']:
	    		x = loc[0]
	    		y = loc[1]
	    		z = loc[2]
	    		vel = m[0]
	    		vel_unit = m[1]
	    		temp = m[2]
	    		temp_unit = m[3]
	    		time = m[4]
	    		out_list.append([x,y,z,time,vel,vel_unit.strip(),temp,temp_unit.strip(),percent_num,percent])
	return out_list

def write_file_csv(lst,filename = os.path.join('results','all_data.csv')):
	f = open(filename,'w')
	for l in lst:
		for thing in l:
			f.write(str(thing))
			f.write(',')
		f.write('\n')
	f.close()

def empty_folder(mypath):
	for root, dirs, files in os.walk(mypath):
	    for file in files:
	        os.remove(os.path.join(root, file))

if __name__ == "__main__":
	generate_data = True
	make_pictures = True

	if generate_data:
		all_out = []
		all_out.append(['x','y','z','time','velocity','velocity unit','temperature','temperature unit','percent wind tunnel','string comment'])
	
	if make_pictures:
		empty_folder(os.path.join('results','slikice_skupaj'))
		empty_folder(os.path.join('results','slikice_absolute_skupaj'))


	for folder in glob.glob(os.path.join('meritve',"meritve_*")):
		if make_pictures:
			empty_folder(os.path.join(folder,'slikice'))
			empty_folder(os.path.join(folder,'slikice_absolute'))
			izris(folder)
			for file_slikica in glob.glob(os.path.join(folder,'slikice','*.png')):
				head, tail = os.path.split(file_slikica)
				shutil.copyfile(file_slikica,os.path.join('results','slikice_skupaj',tail))
			for file_slikica_absolute in glob.glob(os.path.join(folder,'slikice_absolute','*.png')):
				head, tail = os.path.split(file_slikica_absolute)
				shutil.copyfile(file_slikica_absolute,os.path.join('results','slikice_absolute_skupaj',tail))

		if generate_data:
			out = get_data(folder)
			all_out += out

	write_file_csv(all_out)
