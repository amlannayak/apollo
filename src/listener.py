'''
	@project: Atlas
	@file: listener.py
	@objective: receives audio and converts to text commands
	@author: Amlan Nayak

	Extended from uberi/speech_recognition example
'''
import speech_recognition as sr
import sys, time, random, os
import spotify_client as sp_client 
import oauth2
from spotipy import Spotify
from collections import defaultdict 

_WIT_AI_KEY = "GP3LO2LIQ2Y4OSKOXZN6OAOONB55ZLN5"
_OAUTH_TOKEN= sp_client.get_oauth_token()
_CSRF_TOKEN = sp_client.get_csrf_token()
_USER = "nayakam"

_CI = os.getenv('SPOTIPY_CLIENT_ID')
_CS = os.getenv('SPOTIPY_CLIENT_SECRET')

def asay(msg):
	print("@apollo: " + msg)
def usay(msg):
	print("@me: " + msg)

auth = oauth2.SpotifyClientCredentials(client_id=_CI, client_secret=_CS)
asay("Getting access token")
_AUTH = auth.get_access_token()
_SP = Spotify(auth=_AUTH)
_PLAYLISTS = _SP.user_playlists(user=_USER)
# List of track URI's to enable "skipping"
global _CURR_TRACK_LIST 
# Number of items to return from track search
_TLIMIT = 10
# Number of items to return from playlist search
_PLIMIT = 100

# Dictionary of playlist URI's with names as keys
_PLAYLIST_DICT = defaultdict(lambda: defaultdict(lambda: '0'))
for item in _PLAYLISTS.items()[0][1]:
	name = item['name'].lower()
	_PLAYLIST_DICT[name]['uri'] = item['uri']
	_PLAYLIST_DICT[name]['id'] =  item['id']


def parseCommand(phrase):
	'''
		Parses transcribed phrase into command keywords
		Currently supports 3 command classes: 
			1:
				- "Play/Pause"				
				- "Skip this song"
				- "Play previous/last song"
			2:
				- "Play <song>"
				- "Play <song> by <artist>"
				- "Play playlist <playlist>"
			3:
				- "Add this song to playlist <playlist>"

		@param phrase: transcribed phrase received from
			captured_audio instance
	'''
	cmd  = []
	phrase = phrase.lower()
	if(phrase == "play"):
		cmd.append((1,"play"))
	elif(phrase == "pause"):
		cmd.append((1,"pause"))
	elif("skip" in phrase):
		cmd.append((1,"skip"))
	elif("previous" in phrase or "last" in phrase):
		cmd.append((1, "prev"))
	elif("play" in phrase):
		cmd.append((2, phrase))
	elif("by" in phrase):
		keywords = phrase.replace("play ","").split("by")
		cmd.append((2,keywords))
	elif("play" in phrase and "playlist" in phrase):
		cmd.append((2, phrase.split("play ")[-1]))
	asay("Sending request to Spotify")
	sendRequest(cmd)

def sendRequest(command):
	'''
		Sends appropriate request to Spotify
		@param command: parsed command string 
	'''
	if(len(command) == 0):
		asay("Error: Command was empty")
		return
	global _CURR_TRACK_LIST
	key = command[0][0]
	cmd = command[0][1]
	asay("key: %i\t command: %s"%(key, str(cmd)))
	if(key == 1):
		if(cmd == "play"):
			sp_client.unpause(_OAUTH_TOKEN, _CSRF_TOKEN)
			asay(">> Play")
		elif(cmd == "pause"):
			sp_client.pause(_OAUTH_TOKEN, _CSRF_TOKEN)
			asay("|| Paused")
		elif("skip" in cmd or "next" in cmd):
			if(len(_CURR_TRACK_LIST) == 0):
				asay("Empty track list! Play a song to populate tracklist")
				return 
			track_number = random.randint(0, len(_CURR_TRACK_LIST))
			sp_client.play(_OAUTH_TOKEN, _CSRF_TOKEN, _CURR_TRACK_LIST[track_number])

	elif(key == 2):
		# Play playlist
		if("playlist" in cmd):
			req_playlist = cmd.split("playlist ")[-1]
			playlist_uri = _PLAYLIST_DICT[req_playlist]['uri']
			playlist_id = _PLAYLIST_DICT[req_playlist]['id']
			if(playlist_uri == '0'):
				asay("Couldn't find playlist " + req_playlist)
				return
			else:
				sp_client.play(_OAUTH_TOKEN, _CSRF_TOKEN, playlist_uri)
				playlist_tracks = _SP.user_playlist_tracks(user=_USER, playlist_id=playlist_id)
				_CURR_TRACK_LIST = [item['track']['uri'] for item in playlist_tracks['items']]
		# Play single track
		else:
			# Artist name only
			if("artist" in cmd):
				artist = cmd.split("artist")[-1]
				asay("Looking for " + str(artist))
				result = _SP.search(q=artist, type='artist', limit=_TLIMIT)
				asay("Playing " + str(result['artists']['items'][0]['name']))
				artist_uri = result['artists']['items'][0]['uri']
				sp_client.play(_OAUTH_TOKEN, _CSRF_TOKEN, artist_uri)
				return
			# Track + Artist name provided
			elif("by" in cmd):
				track = cmd[0]
				artist = cmd[-1]
				asay("Looking for " + str(artist) + ":" + str(track))
				result = _SP.search(q=track+" "+artist, type='track', limit=_TLIMIT)
			# Track name only
			else:
				track = cmd[0]
				asay("Looking for " + str(track))
				result = _SP.search(q=track, type='track', limit=_TLIMIT)
			try:
				track_uri = result['tracks']['items'][0]['uri']				
				sp_client.play(_OAUTH_TOKEN, _CSRF_TOKEN, track_uri)
				album_uri = result['tracks']['items'][0]['album']['uri']
				album_tracks = _SP.album_tracks(album_id=album_uri)
				_CURR_TRACK_LIST = [item['uri'] for item in album_tracks['items']]
			except KeyError or IndexError:
				asay("Couldn't find URI")
				return
		

def capture():
	r = sr.Recognizer()
	m = sr.Microphone()

	# Adjusting to ambient noise level
	asay("Hi! I'm Apollo!")
	with m as source:
		asay("Let me adjust the mic really quick")
		#r.adjust_for_ambient_noise(source)
		r.energy_threshold = 4000
		asay("Say 'hello' to adjust mic level")
		audio = r.listen(source)
	return callback(r, audio)

def callback(recog, audio):
	'''
		Listener thread calls this when a phrase is detected
		Saves response in self.command variable
		@param recog: recognizer object
		@param audio: phrase captured from device
	'''
	asay("I heard something!")
	try:
		phrase = recog.recognize_wit(audio, key=_WIT_AI_KEY)
		usay(phrase)
		return phrase
	except sr.UnknownValueError:
		print("Wit.ai could not understand audio")
	except sr.RequestError as e:
		print("Could not request results from Wit.ai service; {0}".format(e))


def main():
	'''
		Main listening loop (runs until explicitly killed)
	
	r = sr.Recognizer()
	m = sr.Microphone()

	# Adjusting to ambient noise level
	asay("Hi! I'm Apollo!")
	with m as source:
		asay("Let me adjust the mic really quick")
		r.adjust_for_ambient_noise(source)
		asay("Say 'hello' to adjust mic level")
		audio = r.listen(source)

	r.energy_threshold = 4000
 	stop_listening = r.listen_in_background(m, callback)
 	'''
 	# Busy loop while background thread listens
 	time.sleep(2)
 	asay("... waiting for command ...")
	while True:
		command = capture()
		parseCommand(command)

if __name__ == "__main__":
	main()
