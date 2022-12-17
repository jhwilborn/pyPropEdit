from os import path, listdir
import subprocess, json
from dataclasses import dataclass
import time
import asyncio

"""
	Provides two classes: File and Track, which store metadata about files and tracks, respectively
	Provides a number of functions:
	kb_interrupt - generic function for making a less ugly keyboard interrupt message
	get_paths - takes a directory and returns True and list of file strings or False
	remove_invalid_files - takes list of strings and returns a list of strings excluding matched cases
	process_tracks - takes a file and returns a list of track objects
	get_data - takes a file path and parent path and returns file metadata
	get_data_async - runs get_data asynchnronously
	make_files - takes a list of file paths and their parent directory and returns a sorted list of file objects
"""
@dataclass(slots=True)
class File:
	filename: str
	absolute_path: str
	data: dict
	def __str__(self):
		return f"""filename:{self.filename} | absolute_path:{self.absolute_path}\n data:{self.data}\n""" 

@dataclass(slots=True)
class Track:
	type: str
	number: int
	lang: str
	default: bool
	trackname: str = 'none'
	def __str__(self):
		return f'''track:{self.number} | {self.type} | lang: {self.lang} | default: {self.default} | track name: {self.trackname}'''

# get_paths() takes a typed user-inputted directory string and returns all of the files in that directory
def kb_interrupt():
	print("\nKeyboard Interrupt, exiting...")
	exit(0)

def get_paths(directory: str) -> tuple:
	try:
		directory = directory.strip()
		files = [f for f in listdir(directory) if path.isfile(path.join(directory, f))]
		return (True, files)
	except FileNotFoundError:
		print("Invalid directory, try again.\n")
		return (False)

# remove_invalid() generates a new validated list without designated values 
def remove_invalid_files(files: list) -> list:
	try:
		files = [f for f in files if ('._' or '.ds_store') not in f.lower() and '.mkv' in f.lower()]
		if len(files) == 0:
			raise FileNotFoundError
	except FileNotFoundError:
		print("No compatible files found in directory. Exiting...")
		exit(1)
	return files

# process_tracks takes a list of unprocessed tracks and throws away unnecessary information
def process_tracks(unp_tracks: list) -> list:
	tracklist = list()
	for track in unp_tracks:
		properties = track['properties']
		match (properties['codec_id']).split('_')[0]: #split the codec_id on the a/v/s identifier and give them appropriate track types
				case 'A':
					tracktype = "audio"
				case 'V':
					tracktype = "video"
				case 'S':
					tracktype = "subtitle"
		trackname="none"
		if 'track_name' in properties: # if a track has a name, set it
			trackname = properties['track_name']
		tracklist.append(Track(tracktype, properties['number'], properties['language'], bool(properties['default_track']), trackname))
	return tracklist

# get_data() constructs an absolute path to a file and runs the shell command mkvmerge -J to get json data about an MKV file and returns a File object
def get_data(file_path: str, parent_path: str) -> File:
	try:
		absolute_path = path.join(parent_path, file_path)
		response = subprocess.run(['mkvmerge', '-J', absolute_path], stdout=subprocess.PIPE, universal_newlines=True)
		metadata = json.loads(response.stdout)
		if 'tracks' not in metadata:
			raise KeyError
		unprocessed_tracks = metadata['tracks']
		data = process_tracks(unprocessed_tracks)
		return File(file_path, absolute_path, data)
	except KeyError:
		print("KeyError, make sure that only .mkv files have been sent")

# get_data_async() asynchronously runs get_data()
async def get_data_async(file_path, parent_path) -> list:
	return await asyncio.to_thread(get_data, file_path, parent_path)

# make_files() takes a list of validated .mkv file paths and asynchronously aquires the mkv metadata
async def make_files(files_paths: list, directory: str) -> list:
	try:
		if len(directory) == 0:
			raise NameError
		print("Getting metadata, this will take a second.")
		timer_start = time.perf_counter()
		results = await asyncio.gather(*[get_data_async(file, directory) for file in 
		files_paths])
		timer_end = time.perf_counter()
		time_result = (timer_end - timer_start)
		print(f"Time: {time_result:0.5f}s")
		results.sort(key=lambda x:x.filename)
		return results
	except KeyboardInterrupt:
		kb_interrupt()
	except NameError:
		print("Global directory was not correctly set. What did you do...?")
		exit(1)

async def main() -> None:
	try:
		validated_directory = str()
		paths = list()
		while True:
			directory = input("Enter path to directory: ")
			paths_tup = get_paths(directory)
			if paths_tup[0]:
				validated_directory = paths_tup[1]
				paths = paths_tup[2]
				break;
		validated_paths = remove_invalid_files(paths)

		file_objs = await make_files(validated_paths, validated_directory)
		print(*file_objs, sep='\n')
	except KeyboardInterrupt:
		kb_interrupt()
	except AttributeError as AE:
		print("NoneType Error. The directory was not correctly handled in make_files", AE)
		exit(1)

if __name__ == "__main__":
	asyncio.run(main())


	# do_percentage() calculates iterations of track processing in get_data using GVs
# def do_percentage():
# 	percent = (percentage_count/percentage_max)*100
# 	percentage_count = percentage_count + 1
# 	print(str(int(percent))+'%')
