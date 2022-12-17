import asyncio
import get_files
from dataclasses import dataclass
import argparse
import handle_tracks
from get_files import File

"""
Parses command line option for batch, then runs functions from get_files and handle_tracks
ask_for_tracks - takes a list of tracks and asks for user input. If user input is valid, returns the selections
select_tracks - handles making the track list, asking for selection, and making commands. Returns commands
"""

# Parse whether the main.py invocation should be in batch mode
parser = argparse.ArgumentParser(
	prog="pyPropEdit.py",
	description="Accepts a user-inputted directory. Allows changing of the default subtitle and audio tracks of .mkv files in the provided directory.", 
	formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-b", "--batch", action="store_true", help="b(l)a(s)tch processing")
batch = vars(parser.parse_args())['batch']
print("batch mode?", batch)

# When you pass a list of tracks, it will prompt the user to pick one for audio and one for subtitles, and then return those selections in a list
def ask_for_tracks(tracklist: list) -> tuple:
	tracktypes = ('audio', 'subtitle')
	selections = list() # establish selection list
	while True:
		selections = [] # reset selection list on every loop
		for tracktype in tracktypes:
			while True:
				select = input(f"Pick {tracktype} track number: ")
				if handle_tracks.check_valid_track(select, tracktype, tracklist):
					selections.append(select) # add the selected tracks to the selections list
					break # exit if valid, reloop if not
		print("Selected Tracks: \n"+str(tracklist[int(selections[0])-1])+'\n'+str(tracklist[int(selections[1])-1]))
		if batch:
			confirm = input("Warning, you are in batch mode. Changes will be applied to all .mkv files in the folder. Y/N: ")
		else:
			confirm = input("Are you sure you want these tracks? Y/N: ")
		if confirm.lower() == "y":
			break; # exit loop if user confirms
	return selections

def select_tracks(file: type[File]) -> str and str:
	print("Name:", file.filename)
	tracklist = handle_tracks.build_tracklist(file)
	print (*tracklist, sep='\n')
	selections = ask_for_tracks(tracklist) # This is done in main.py bc we are asking for user input
	reset, update = handle_tracks.make_commands(file.absolute_path, selections, len(tracklist))
	return reset, update

async def main():
	try:
		validated_directory = str()
		paths = list()
		while True: # make sure directory is valid
			directory = input("Enter path to directory: ")
			paths_tup = get_files.get_paths(directory)
			if paths_tup[0]: # if true
				validated_directory = directory
				paths = paths_tup[1] # paths
				break;
		validated_paths = get_files.remove_invalid_files(paths) # remove detritus
		file_objs = await get_files.make_files(validated_paths, validated_directory)
		if batch:
			reset, update = select_tracks(file_objs[0]) # build commands based on first file
			await asyncio.gather(*[handle_tracks.process_tracks_async(file.filename, reset, update) for file in file_objs])
		else:
			for file in file_objs:
				reset, update = select_tracks(file)
				handle_tracks.process_tracks(file.filename, reset, update)			
	except KeyboardInterrupt:
		get_files.kb_interrupt()
	except AttributeError as AE:
		print("NoneType Error. The directory was not correctly handled in make_files", AE)
		exit(1)

if __name__ == "__main__":
	asyncio.run(main())
