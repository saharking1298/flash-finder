# flash-finder

## Description
This little program finds you a flash game (.swf file) on a given URL , downloads it and launches it for you!

## Installation
- Clone the github repository.
- Install the dependencies - "`pip install -r requirements.txt`", strongly recommended on a virtual environment.
- Open and run the main Python file - "`py FlashFinder.py`"

## Usage
- To use the script, all you need to do is enter the URL of the page that used to have a flash game on it.  
- The program will scan the page to find links for swf files (flash executables).
- If there is one, the script will download it to the game library (Located in '`Games`' folder), and launch it using the flashplayer executable in '`Bin`' Folder.

### Having problems?
If the script crashes, it always keeps a record of the last error traceback in '`Logs/LatestLog.txt`'.  
Please check it and if it's the script's fault (and the page is not broken), please create an issue ticket.

### Contributions are welcomed!
If you have any idea how to make this script even better, please contact me or send a pull request!


