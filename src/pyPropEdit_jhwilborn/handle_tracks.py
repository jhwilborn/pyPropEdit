import subprocess
from get_files import File
import asyncio

"""
	Provides functions to handle creating lists of tracks, checking their validity, generating the commands to change defaults, and executing commands to change defaults
	build_tracklist - takes a file and returns a list of its tracks
	check_valid_track - takes a selection number, a track type, and tracklist and returns T/F
	defaultZero/One - takes track number and returns string with partial commands
	make_commands - takes file's absolute path, track selections, and the number of total tracks and returns correctly formatted shell commands to change files
	process_tracks - executes provided commands in the shell
	process_tracks_async - runs process_tracks asynchronously
"""

def build_tracklist(file: type[File]) -> list:
	tracklist = list()
	for track in file.data:
		tracklist.append(track)
	return tracklist

def check_valid_track(selected_number, tracktype, tracklist):
	# print(tracklist)
	valid_tracks = list()
	track_count = len(tracklist) # Get the number of tracks
	for track in tracklist: #loop over tracklist
		if track.type == tracktype: #if the track type matches the specified type
			valid_tracks.append(track.number) #add the track to valid_tracks
	#if chain that checks various conditions to determine validity
	if not selected_number.isdigit(): # if selection is not NaN
		print("Entered value",'"'+selected_number+'"',"is not a number")
		return False
	elif int(selected_number) - 1 == 0: # if selection is first element of list
		print("Cannot select the video track")
		return False
	elif int(selected_number) > track_count: # if selected_number is greater than the number of tracks
		print("Entered number is not a track number")
		return False
	elif int(selected_number) not in valid_tracks: # if track is the wrong type
		print("Incorrect track type selected. Must be", tracktype, "track")
	else:
		return True


def defaultZero(tracknum):
			return f"--edit track:{tracknum} --set flag-default=0 "
def defaultOne(tracknum):
			return f"--edit track:{tracknum} --set flag-default=1 "

def make_commands(absolute_path: str, selections: list, track_count: int) -> str and str:
	mkvpropedit_reset = str()
	for i in range(1, track_count):
		mkvpropedit_reset+=defaultZero(i+1) # Track numbers start at 1, need to exclude video track
	mkvpropedit_new_defaults = defaultOne(selections[0])+defaultOne(selections[1])
	reset = ['mkvpropedit '+f"'{absolute_path}'"+' '+mkvpropedit_reset]
	update = ['mkvpropedit '+f"'{absolute_path}'"+' '+mkvpropedit_new_defaults]
	return reset, update

def process_tracks(filename: str, reset: str, update: str) -> None:
	reset_results = subprocess.run(reset, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
	update_results = subprocess.run(update, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
	print("Changes made to", filename)

async def process_tracks_async(filename: str, reset: str, update: str) -> None:
	await asyncio.to_thread(process_tracks, filename, reset, update)

if __name__ == "__main__":
	print("Not intended to be run directly. Exiting.")
	exit(1)