import getFiles
import subprocess

# Create a Track object to be created for each track in a file
class Track:
	def __init__(self, type: str, number: int, lang: str, default: bool, trackname = 'none'):
		self.type = type
		self.trackname = trackname
		self.number = number
		self.lang = lang
		self.default = default
	def __str__(self):
		return f'''track:{self.number} | {self.type} | lang: {self.lang} | default: {self.default} | track name: {self.trackname}'''

# Main function of the file. Expects a single file object
def handleTracks(file, batch_check):
	try:
		### SETUP VARIABLES ###
		tracks = file.details_dict['tracks'] # Get tracks key from File
		abspath = file.absolute_path # Get target directory/abspath
		tracklist = list()
		# Set selected defaults to None
		audio_select = None 
		subtitle_select = None

		# two while loops infinitely asking for valid user input
		def inputLoop():
			# Establish nonlocal variables from parent function to be assigned by input
			nonlocal audio_select
			nonlocal subtitle_select
			while True:
				audio_select = (input('Which audio track should be the default? Enter a number: '))
				if check_valid(audio_select, "audio"): 
					break
			while True:
				subtitle_select = (input('Which subtitle track should be the default? Enter a number: '))
				if check_valid(subtitle_select, "subtitle"): 
					break
		
		# Function to establish validity of user input. Accepts input of subtitle/audio_select and t(rac)k type. Local vars means that it will establish acceptable track types for audio, then for subtitles, respectively and distinctly
		def check_valid(selector, tkType):
			valid_tracks = list()
			nonlocal tracklist # Pull tracklist from parent function
			track_count = len(tracklist) # Get the number of tracks
			for track in tracklist: #loop over tracklist
				if track.type == tkType: #if the track type matches the specified type
					valid_tracks.append(track.number) #add the track to valid_tracks
			#if chain that checks various conditions to determine validity
			if not selector.isdigit(): # if selection is not NaN
				print("Entered value",'"'+selector+'"',"is not a number")
				return False
			elif int(selector) - 1 == 0: # if selection is first element of list
				print("Cannot select the video track")
				return False
			elif int(selector) > track_count: # if selector is greater than the number of tracks
				print("Entered number is not a track number")
				return False
			elif int(selector) not in valid_tracks: # if track is the wrong type
				print("Incorrect track type selected. Must be", tkType, "track")
			else:
				return True
		# functions to create mkvpropedit commands with a provided track number
		def defaultZero(tracknum):
			return f"--edit track:{tracknum} --set flag-default=0 "
		def defaultOne(tracknum):
			return f"--edit track:{tracknum} --set flag-default=1 "
		
		# parse the properties of each track in tracks
		for track in tracks:
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
			# Create a Track with its properties and append it to the tracklist
			tracklist.append(Track(tracktype, properties['number'], properties['language'], bool(properties['default_track']), trackname))

		print("Editing file:", file.filename) # Print out the filename
		print (*tracklist, sep='\n') 	# Print out the list of formatted track objects
		
		# If this iteration is not in batch mode, run the normal process to ask for user input
		if not batch_check:
			inputLoop()
			# Infinitely check if the user has approved their selected tracks
			while True:
				print("Selected Tracks: \n"+str(tracklist[int(audio_select)-1])+'\n'+str(tracklist[int(subtitle_select)-1]))
				check_input = input("Are you sure you want these tracks? Y/N: ")
				#There is a bug in python where using an OR in a condition in the while loop accepts ANYTHING as having met that condition.
				if check_input.lower() == "y":
					break
				else:
					inputLoop()

			mkvpropedit_reset = str()
			# For every item in tracklist excluding the video track, generate a string mkvpropedit_reset command that will set all of the tracks to default=false
			for i in range(1, len(tracklist)):
				mkvpropedit_reset+=defaultZero(tracklist[i].number)  
		
			# Create string that applies defaults to selected audio and sub track
			mkvpropedit_new_defaults = defaultOne(audio_select)+defaultOne(subtitle_select)
			

		# Create full command strings from mkvpropedit, the absolute path of the file, and the appropriate propedit commands
			reset = ['mkvpropedit '+f"'{abspath}'"+' '+mkvpropedit_reset]
			update = ['mkvpropedit '+f"'{abspath}'"+' '+mkvpropedit_new_defaults]

			# Set the global selectors to be used in batch mode
			global_select.append(reset)
			global_select.append(update)

		# If batch mode is enabled, use the global selectors, otherwise use file-specific selectors
		if batch_check:
			reset_results = subprocess.run(global_select[0], stdout=subprocess.PIPE, universal_newlines=True, shell=True)
		# Then run the update command
			update_results = subprocess.run(global_select[1], stdout=subprocess.PIPE, universal_newlines=True, shell=True)
		else:
			# First run the reset command
			reset_results = subprocess.run(reset, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
			# Then run the update command
			update_results = subprocess.run(update, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
			# Print the command results
		print("mkvpropedit reset command:", reset_results.stdout+'\n'+"mkvpropedit update command:",update_results.stdout)

	except KeyboardInterrupt:
		print(" Keyboard interrupt detected, exiting")
		exit(1)


if __name__ == "__main__":
	# Setup vars for batch processing
	batch = bool()
	global_select = list()
	# Ask if user wants batch mode until they enter valid input
	while True:
		try:
			batch_mode = input("Start in batch mode? Y/N: ").lower()
			valid = {"y", "n"}
			if batch_mode not in valid:
				raise ValueError # Throw excep, retry
			else:
				if batch_mode == "y": batch = True
				if batch_mode == "n": batch = False
				break
		except ValueError:
			print("Invalid value entered, try something else")
		except KeyboardInterrupt:
			print(" Keyboard interrupt detected, exiting")
			exit(1)



	rawFiles = getFiles.handle_files()
	for i in range(len(rawFiles)):
		# If it's the first track, batch is always off
		if i < 1:
			handleTracks(rawFiles[i], False)
		# If it's after the first track, batch could be on or off.
		else:
			handleTracks(rawFiles[i], batch)
	print('The script has finished. Exiting...')
