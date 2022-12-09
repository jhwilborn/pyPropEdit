from os import path, listdir
import subprocess, json

# Define a class File to store a name, an absolute path, and a dictionary
class File:
	def __init__(self, filename: str, absolute_path:str, details_dict:dict):
		self.filename = filename
		self.absolute_path = absolute_path
		self.details_dict = details_dict
	def __str__(self):
		return f"""filename:{self.filename} | absolute_path:{self.absolute_path}\n details_dict:{self.details_dict}
		""" 

# Define a function to query the requested directory and create a list of sorted files, which will then be passed to mkvmerge to extract metadata
# Iterate over every file in the list
# Convert the extract json to a python dictionary, and store it in a File object
# Return a list of the File objects
def handle_files():
	directory = input("Search directory: ")
	files = list()
	while True:
		directory = directory.strip()
		try:
			files = [f for f in listdir(directory) if path.isfile(path.join(directory, f))]
			break
		except FileNotFoundError:
			directory = input("Invalid path, try again: ")

	# Remove macOS's pesky .DS_Store file if it exists
	if '.DS_Store' in files:
		files.remove('.DS_Store') 
	for item in files:
		if '.mkv' not in item.lower():
			files.remove(item)
	files = sorted(files) # Sort the files
	results = list()
	for file in files:
		absolute_path = path.join(directory, file) # Join to create abspath
		shell_call = subprocess.run(['mkvmerge', '-J', absolute_path], stdout=subprocess.PIPE, universal_newlines=True)
		results_dict = json.loads(shell_call.stdout) # process json to dict
		results.append(File(file, absolute_path, results_dict)) #append res

	# print(*results, sep='\n')
	return results
