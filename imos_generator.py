#!/usr/bin/python
import sys, os, operator, math, getopt
import xlsxwriter

class GaussianLog(object):
	"""docstring for GaussianLog"""
	def __init__(self, filename):
		super(GaussianLog, self).__init__()
		self.ATOM_NAME=["H","C","O","N","F","Cs","Na","Cl","I","K","Rb","P","Ca","Li","S","Fr","Be","Mg","U","Sr","Ba","Ra","B","Al","Ga","In","Tl","Si","Ge","Sn","Pb","As","Sb","Bi","Se","Te","Po","Br","At","He","Ne","Ar","Kr","Xe","Rn","Fe","Au","Ag","Ni","Cr","Cu","Mn","Hg","Other"]
		self.ATOM_RADII=[1.1,1.7,1.52,1.55,1.47,3.43,2.27,1.75,1.98,2.75,3.03,1.8,2.31,1.81,1.8,3.48,1.53,1.73,2.31,2.49,2.68,2.83,1.92,1.84,1.87,1.93,1.96,2.1,2.11,2.17,2.02,1.85,2.06,2.07,1.9,2.06,1.97,1.83,2.02,1.4,1.54,1.88,2.02,2.16,2.2,1.4,1.66,1.72,1.63,1.4,1.4,1.4,1.55,2]
		self.ATOM_NUMBER=[1,12,16,14,19,133,23,35,127,39,85,31,40,7,32,223,9,24,238,88,137,226,11,27,70,115,204,28,73,119,207,75,122,209,79,128,212,80,210,4,20,40,84,131,222,56,197,108,59,52,64,55,201,400]
		self.filename = filename
		self.last_matrix = []
		self.where_are_matrices = []
		self.initial_matrix_position = 0
		self.file_content = []
		self.atoms = []
		self.number_of_atoms = 0
		self.final_matrix = []
		self.charge = 0
		self.multiplicity = 0
		self.calculation_commands = ""
		self.is_counterpoise = 0
		self.nbo_charges = []
		self.atoms_radii = []
		self.atoms_numbers = []
		self.total_mass = 0

		with open(self.filename, 'r') as file:
			self.file_content = file.readlines()

		for index, line in enumerate(self.file_content):
			if '#' in line: self.calculation_commands = line
			if 'Symbolic Z-matrix:' in line: self.initial_matrix_position = index+2
			if 'Coordinates (Angstroms)' in line: self.where_are_matrices.append(index+3)
			if 'Charge =' in line:
				self.charge = int(line.split("=")[1].split()[0])
				self.multiplicity = int(line.split("=")[2].split()[0])
			if 'Summary of Natural Population Analysis:' in line:
				self.nbo_charges = self.get_nbo_charges(index+6)

		if ('counterpoise' in self.calculation_commands) or ('Counterpoise' in self.calculation_commands):
			self.is_counterpoise = 1
			self.initial_matrix_position = self.initial_matrix_position + 2
			

		self.atoms = self.get_atoms_from_initial_matrix()
		self.number_of_atoms = len(self.atoms)
		
		self.last_matrix = self.get_last_matrix()

		for index, coordinate in enumerate(self.last_matrix):			
			self.final_matrix.append([self.atoms[index]] + coordinate)

		self.atoms_radii = self.get_atoms_radii()

		self.atoms_numbers = self.get_atoms_numbers()
		self.total_mass = sum(self.atoms_numbers)

		current_folder_path = os.path.dirname(os.path.abspath(__file__))
		new_folder_path = os.path.dirname(os.path.abspath(__file__))+"/"+self.filename.split(".")[0]
		os.mkdir(new_folder_path)

		# print self.final_matrix

	def get_atoms_from_initial_matrix(self):
		result = []

		for line in self.file_content[self.initial_matrix_position:]:
			if len(line.strip()) == 0: break
			result.append(line.strip().split(" ")[0])
		return result		
	
	def get_last_matrix(self):
		result = []
		#print self.where_are_matrices
		#print self.number_of_atoms

		for line in self.file_content[self.where_are_matrices[-1]:self.where_are_matrices[-1]+self.number_of_atoms]:
			dash_count = line.count('-')
			#print line
			if dash_count > 6: break
			linia = line.strip().split()
			filter(None, linia)			
			result.append([linia[3], linia[4], linia[5]])
		return result

	def get_nbo_charges(self,line_number):
	 	result = []

		for line in self.file_content[line_number:]:
			if len(line.strip()) == 0: break
			if '=======' in line: break
			line_data = filter(None, line.strip().split(" "))
			result.append(line_data[2])
		return result

	def get_atoms_radii(self):
		result = []

		for atom in self.atoms:
			index = self.ATOM_NAME.index(atom)
			result.append(self.ATOM_RADII[index])
		return result

	def get_atoms_numbers(self):
		result = []

		for atom in self.atoms:
			index = self.ATOM_NAME.index(atom)
			result.append(self.ATOM_NUMBER[index])
		return result

class Excel(object):
	"""docstring for Excel"""
	def __init__(self, gauss_log):
		super(Excel, self).__init__()
		self.gauss_log = gauss_log
		workbook = xlsxwriter.Workbook(gauss_log.filename.split(".")[0]+"/"+gauss_log.filename.split(".")[0]+".xlsx")
		worksheet = workbook.add_worksheet()

		# kolumna 1, 2, 3, 4
		row = 0
		col = 0
		for name, x, y, z in self.gauss_log.final_matrix:
			worksheet.write_string  (row, col, name)
			# worksheet.write_datetime(row, col + 1, date, date_format )
			worksheet.write_number  (row, col + 1, float(x))
			worksheet.write_number  (row, col + 2, float(y))
			worksheet.write_number  (row, col + 3, float(z))
			row += 1
		# kolumna 5
		row = 0
		for radii in self.gauss_log.atoms_radii:
			worksheet.write_number  (row, col + 4, float(radii))
			row += 1
		# kolumna 6
		row = 0
		for charge in self.gauss_log.nbo_charges:
			worksheet.write_number  (row, col + 5, float(charge))
			row += 1
		# kolumna 7
		row = 0
		worksheet.write_string  (0, col + 6, "TOTAL z")
		worksheet.write_number  (1, col + 6, int(self.gauss_log.charge))
		worksheet.write_string  (2, col + 6, "Totalmass")
		worksheet.write_number  (3, col + 6, int(self.gauss_log.total_mass))
		# kolumna 8
		row = 0
		for number in self.gauss_log.atoms_numbers:
			worksheet.write_number  (row, col + 7, int(number))
			row += 1

		workbook.close()

class ImosCla(object):
	"""docstring for ImosCla"""
	def __init__(self, gauss_log, gas):
		super(ImosCla, self).__init__()
		self.gauss_log = gauss_log
		self.gas = gas

		self.save_file()

	def save_file(self):
		save_file = []
		filename = self.gauss_log.filename.split(".")[0]	

		save_file.append("excelfile          Savefile           Gas\n")
		save_file.append(filename + ".xlsx" + " " + filename + ".imos" + "       " + self.gas.name + "\n")		

		save_file.append("\n")
		save_file.append("interface 0 0\n")
		save_file.append("fromvalue 1\n")
		save_file.append("tovalue 1\n")
		save_file.append("Charge " + str(self.gauss_log.charge) + "\n")
		save_file.append("Mgas " + str(self.gas.mgas) + "\n")
		save_file.append("radgas " + str(self.gas.radgas) + "\n")
		save_file.append("Polarizability " + str(self.gas.polarizability) + "\n")
		save_file.append("Pressure 526\n")
		save_file.append("Mweight " + str(self.gauss_log.total_mass) + "\n")
		save_file.append("Temperature 300\n")
		save_file.append("\n")
		save_file.append("NrotationsTM 3\n")
		save_file.append("NgastotalEHSS 300000\n")
		save_file.append("NgastotalTM 2000000\n")
		save_file.append("Acommodation 1.0\n")
		save_file.append("reemvel 1\n")
		save_file.append("\n")
		save_file.append("PA 0\n")
		save_file.append("EHSS/DHSS 0\n")
		save_file.append("TM 1\n")
		save_file.append("DTM 0\n")
		save_file.append("\n")
		save_file.append("SimplifiedTM 1\n")
		save_file.append("LennardJones 1\n")
		save_file.append("qpol 0\n")
		save_file.append("TDHSS 0\n")
		save_file.append("Cutoff 0\n")
		save_file.append("Diffuse? 1\n")
		save_file.append("\n")
		save_file.append("seed 17\n")
		save_file.append("Numthreads 8\n")
		save_file.append("\n")
		save_file.append("\n")
		save_file.append("\n")
		save_file.append("\n")

		with open(self.gauss_log.filename.split(".")[0]+"/"+"IMoS.cla", 'w') as writefile:
			for line in save_file:
				writefile.write(line)


class Gas(object):
	"""docstring for Gas"""
	def __init__(self, arg):
		super(Gas, self).__init__()
		self.arg = arg
		self.name = arg["name"]
		self.mgas = arg["mgas"]
		self.radgas = arg["radgas"]
		self.polarizability = arg["polarizability"]

class Pbs(object):
		"""docstring for Pbs"""
		def __init__(self, gauss_log_name):
			super(Pbs, self).__init__()
			self.gauss_log_name = gauss_log_name

			self.save_pbs()

		def save_pbs(self):
			save_file = []
			filename = self.gauss_log_name

			save_file.append("#!/bin/bash\n")
			save_file.append("#PBS -S /bin/bash\n")
			save_file.append("#PBS -q short\n")
			save_file.append("#PBS -l nodes=1:ppn=8:imos\n")
			save_file.append("#PBS -l walltime=48:0:0\n")
			save_file.append("#PBS -l mem=1000MB\n")
			save_file.append("#PBS -l cput=100000:00:00\n")
			save_file.append("\n")
			save_file.append("export OMP_NUM_THREADS=16\n")
			save_file.append("\n")
			save_file.append("module load matlab/R2018b\n")
			save_file.append("cd $PBS_O_WORKDIR\n")
			save_file.append("temp_scratch=/scratch/imos$RANDOM\n")
			save_file.append("mkdir $temp_scratch\n")
			save_file.append("cp -r $IMOS_PATH/. $temp_scratch\n")			
			save_file.append("cp IMoS.cla $temp_scratch/IMoS.cla\n")
			save_file.append("cp " + filename + ".xlsx $temp_scratch/" + filename +".xlsx \n")
			save_file.append("cd $temp_scratch\n")
			save_file.append("\n")
			save_file.append("./run_IMos109Linux64.sh $MATLAB_MCR_PATH\n")
			save_file.append("cp *.imos $PBS_O_WORKDIR\n")
			save_file.append("\n")

			with open(filename + "/" + filename + ".pbs", 'w') as writefile:
				for line in save_file:
					writefile.write(line)

class StartAll(object):
	"""docstring for StartAll"""
	def __init__(self, log_files):
		super(StartAll, self).__init__()
		self.log_files = log_files

		self.save_script()

	def save_script(self):
		save_file = []

		save_file.append("#!/bin/bash\n")
		save_file.append("#\n")
		save_file.append("cd " + self.log_files[0].filename.split(".")[0] + "\n")
		save_file.append("qsub " + self.log_files[0].filename.split(".")[0] + ".pbs \n")
		save_file.append("\n")

		for log in self.log_files[1:]:
			save_file.append("cd ../" + log.filename.split(".")[0] + "\n")
			save_file.append("qsub " + log.filename.split(".")[0] + ".pbs \n")

		with open("startall.script", 'w') as writefile:
			for line in save_file:
				writefile.write(line)
		




def main(argv):
	gas_name = ""

	try:
		opts, args = getopt.getopt(argv,"hg:",["gas="])
	except getopt.GetoptError:
		print 'cp_generator.py -g <guest atoms range XX-XX>'
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print 'cp_generator.py -g <gas_name>'
			sys.exit()
		elif opt in ("-g", "--gas"):
			gas_name = arg

	gas_dict = {}
	if gas_name.lower() == "n2":
		gas_dict = { "name": "N2", "mgas": 28.014, "radgas": 1.5, "polarizability": 1.71 }

	if gas_name.lower() == "he":
		gas_dict = { "name": "He", "mgas": 4.0026, "radgas": 1.2, "polarizability": 0.2073 }

	gas = Gas(gas_dict)	

	log_files = []
	for file in os.listdir(os.path.dirname(os.path.abspath(__file__))):
		if file.endswith(".log"):
			log_files.append(GaussianLog(file))

	for log in log_files:
		Excel(log)
		ImosCla(log, gas)
		Pbs(log.filename.split(".")[0])

	StartAll(log_files)

	# for file in counter_files:
	# 	print file.filename + " : " + str(file.second_blank_line)
	# 	with open(file.filename.split(".")[0]+'_FREQ_CP.gjf', 'w') as writefile:
	# 		for line in file.counter_filedata:
	# 			writefile.write(line)
	# 	with open(file.filename.split(".")[0]+'_MGFC.gjf', 'w') as writefile:
	# 		for line in file.mgfc_filedata:
	# 			writefile.write(line)
	# 	with open(file.filename.split(".")[0]+'_GFC.gjf', 'w') as writefile:
	# 		for line in file.gfc_filedata:
	# 			writefile.write(line)

if __name__ == "__main__":
   main(sys.argv[1:])