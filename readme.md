# pyPropEdit 0.2

## Version 0.2 changes (from 0.1.1)
* Completely rewrote core functionality to support asynchronous calls to the filesystem
* Enter batch mode through command line option -b / --batch

## Description

**pyPropEdit** uses **[mkvtoolnix](https://gitlab.com/mbunkus/mkvtoolnix)** to quickly change the default audio and subtitle tracks of all .mkv files in a folder. This tool uses mkvpropedit to make changes rather than mkvmerge, so it doesn't require overwriting files.

*Warning:* Uses subprocess shell=True because it's a lot easier and more reliable. Use at your own risk.

## Requirements
* [mkvtoolnix CLI](https://mkvtoolnix.download/downloads.html)
* [Python 3.10.8](https://www.python.org/downloads/release/python-3111/) (untested on earlier versions, but probably works above 3.7)
		
		brew install --cask mkvtoolnix
		brew install python

## Function
1. Accepts user-inputted directory.
2. Gets a list of all files using os.path and listdir.
3. Runs a shell subprocess with mkvmerge -J to get the properties of the mkv files in the folder.
4. Shows the user a list of all tracks in the file and allows them to select new defaults.
5. Overwrites existing defaults using a shell process with mkvpropedit.

## Limitations
 - Not most efficient way to handle transferring data between Python and the shell.
 - Works on a single folder with no subdirectories.
 - Only one mode of interaction.
 - Limited error handling.
 - Relies on "shell=True" for subprocess.

## To Do
 - Robust error handling.
 - Capture of subdirectories.
 - "Fast" mode that lets the user enter two numbers on the same line and immediately proceeds to the next file to modify.
 - Remove reliance on shell=True subprocess feature.
 - Implement tdqm
 - If no compatible files are in the directory, prompt the user for different location