import socket
import os
import re
from bs4 import BeautifulSoup
import requests


types = ["handfæri", "dragnót", "bein viðskipti", "grásleppa", "byggðakvóti"]

# Variables to replace in the preset files
boat_id = False
boat_name = False
possible_name = False
label_type = 0
fish_type = "Þorskur"

# Checks if internet connection is present
def check_internet():
	try:
		s = socket.create_connection(("1.1.1.1", 53))
		return True
	except OSError:
		pass
	return False


# Extracts buyer id from a string
# If no id is found, The full string is returned
def extract_id(text):
	buyer_id = False
	for word in text.split():
		if word.isdigit():
			buyer_id = word
			break

	if buyer_id:
		return buyer_id
	else: 
		return text

# Looks up a vessel id on the web
def get_vessel_data(vessel_id):
	if vessel_id.isnumeric():
		page = requests.get("https://www.samgongustofa.is/siglingar/skrar-og-utgafa/skipaskra/uppfletting?sq=" + str(vessel_id))
		soup = BeautifulSoup(page.content, "html.parser")
		try:
			name = soup.find("strong", text="Nafn:").parent.find("span").string
			suffix = soup.find("strong", text="Umdæmisstafir:").parent.find("span").contents[0].strip()
			return [name, suffix]
		except:
			return False

# Promts the user to select a label category
def select_category():
	global label_type
	print("Veldu flokk")

	i = 1
	for t in types:
		print("    " + str(i), ". " + t.capitalize(), sep="")
		i+=1

	label_type = input("Flokkur: ")

	# Checks if user input a number
	if label_type.isnumeric():
		# Checks if the number is in the appropriate range
		if int(label_type) - 1 < len(types):
			label_type = int(label_type) - 1
			select_boat_id()
		else:
			print("")
			select_category()
	else:
		if label_type in types:
			label_type = types.index(label_type)
			select_boat_id()
		else:
			select_category()
	
# Prompts the user for a boat id
def select_boat_id():
	global boat_id, boat_name, possible_name
	boat_id = input("Skipaskrárnúmer: ")

	# Checks if the boat id is a number & looks it up on the web
	if boat_id.isnumeric():
		if check_internet():
			data = get_vessel_data(boat_id)
			if data:
				possible_name = data[0].capitalize() + " " + data[1]
				confirm_name()


			else:
				print("Skipaskrárnúmer '" + boat_id + "' ekki á skrá")
				select_boat_name()
		else:
			select_boat_name()
	else:
		print("'" + str(boat_id) + "' er ógilt skipaskrárnúmer!")
		select_boat_id()

# 
def confirm_name():
	global boat_name, possible_name
	print(possible_name)
	correct = input("Er þetta rétt nafn? [y/n]: ")
	if correct.lower() == "y":
		boat_name = possible_name
		create_file()
	elif correct.lower() == "n":
		select_boat_name()
	else:
		confirm_name()

# Prompts the user for a boat name
def select_boat_name():
	global boat_name
	if boat_name == False:
		boat_name = input("Bátur: ")
		if len(boat_name) > 0:
			create_file()
		else:
			boat_name = False
			select_boat_name()


def create_file():
	global boat_name, boat_id, fish_type, label_type
	# Selecting, Opening & reading preset file
	preset_file = "PRESET_BOAT.txt"
	if label_type > 1:
		preset_file = "PRESET_BUYER.txt"
	preset = open(preset_file).read()

	if label_type > 1:
		buyer = input("Kaupandi:")

	# Replacing variables in the preset file
	if label_type == 0 or label_type == 1:
		new_boat = preset.replace("BOAT_NAME", boat_name).replace("BOAT_ID", boat_id)
	elif label_type == 2:
		new_boat = preset.replace("BOAT_NAME", boat_name).replace("BOAT_ID", boat_id).replace("BUYER", buyer)
	elif label_type == 3:
		new_boat = preset.replace("BOAT_NAME", boat_name).replace("BOAT_ID", boat_id).replace("BUYER", buyer).replace("Þorskur", "Grásleppa")
		fish_type = "Grásleppa"
	elif label_type == 4:
		new_boat = preset.replace("BOAT_NAME", boat_name).replace("BOAT_ID", boat_id).replace("BUYER", buyer).replace("Þorskur", "Þorskur - Byggðakvóti")
	

	# Generating the new file name
	if label_type > 1:
		new_file_name = types[label_type].capitalize() + "/" + extract_id(buyer) + " " + boat_name + " - " + fish_type + ".prn"
	else:
		new_file_name = types[label_type].capitalize() + "/" + boat_name + " - " + fish_type + ".prn"

	# Checking if file already exists
	if os.path.exists(new_file_name):
		# Extracting the boat id from the existing file
		existing = open(new_file_name, "r").readlines()
		existing_id = re.findall('"([^"]*)"', existing[46])[0]

		# Checking if boat id matches
		if existing_id == boat_id:
			print("Miði fyrir '" + boat_name + "' er til")
		else:
			print("Miði fyrir '" + boat_name + "' er til með annað skipaskrárnúmer (" + existing_id + ")")
			print("Vinsamlegast veldu annað nafn.")
			print("")
			create_boat()
	else:
		# Creating new file
		new_file = open(new_file_name, "w")
		new_file.write(new_boat)
		new_file.close()

		# Done
		print("'" + new_file_name + "' vistað")

if __name__ == "__main__":
	select_category()