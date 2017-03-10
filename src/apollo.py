'''
	@project: Atlas
	@file: apollo.py
	@objective: - receives audio transcript 
				  from Google Speech API
				- parses transcript into commands
				- uses Spotify APIs to control player
	@author: Amlan Nayak
'''
import sys
import time 
import random
import os
import re
import spotify_client as sp_client 
import oauth2
from spotipy import Spotify
from collections import defaultdict 

def asay(msg):
	print("@apollo: " + msg)
def usay(msg):
	print("@me: " + msg)

class Apollo(object):
	'''
		This object is the main interface between the Google Speech
		transcriber and Spotify. It parses the transcribed text from
		Google into commands, conducts queries with the Spotipy API
		and interfaces with the Spotify desktop app to play music.
	'''
	def __init__(self):
		# Authentication with Spotipy API
		self._SP_USER = "nayakam"
		self._SP_CI = os.getenv('SPOTIPY_CLIENT_ID')
		self._SP_CS = os.getenv('SPOTIPY_CLIENT_SECRET')
		self._SP_CRED = oauth2.SpotifyClientCredentials(client_id=self._SP_CI, client_secret=self._SP_CS)
		self._SP_AUTH = self._SP_CRED.get_access_token()
		self._SP = Spotify(auth=self._SP_AUTH)
		self._SP_OAUTH_TOKEN= sp_client.get_oauth_token()
		self._SP_CSRF_TOKEN = sp_client.get_csrf_token()
		self._SP_PLAYLISTS = self._SP.user_playlists(user=self._SP_USER)
		# Dictionary of playlist URI's with names as keys
		self._SP_PLAYLIST_DICT = defaultdict(lambda: defaultdict(lambda: None))
		# Number of items to return from track search
		self._SP_TLIMIT = 10
		# Number of items to return from playlist search
		self._SP_PLIMIT = 100
		self._TRACK_LIST = []
		self.createPlaylistDict()


	#@classmethod
	def createPlaylistDict(self):
		# Populates the playlist dict
		for item in self._SP_PLAYLISTS.items()[0][1]:
			name = item['name'].lower()
			self._SP_PLAYLIST_DICT[name]['uri'] = item['uri']
			self._SP_PLAYLIST_DICT[name]['id'] = item['id']

	#@staticmethod
	def parseCommand(self, phrase):
		'''
			Parses transcribed phrse from Google Speech into 
			command keywords. Curently supports 3 command classes:
				A: 
					- "Play/Pause"
					- "Skip"
				B:
					- "Play <songname>"
					- "Play <songname> by <artist>"
					- "Play playlist <playlistname>"
				C:
					- "Add this song to playlist <playlistname>"

			@param phrase: transcribed phrase from Google Speech API
		'''
		cmd = defaultdict(lambda: None)
		if(not len(phrase)):
			asay("No command received")
			return None
		phrase = phrase.lower().strip(re.search(r'\b(spotify)\b', phrase))
		if("play" in phrase and len(phrase) <= 2):
			cmd['A'] = "play"
		elif("pause" in phrase or "does" in phrase):
			cmd['A'] = "pause"
		elif("skip" in phrase):
			cmd['A'] = "skip"
		elif("previous" in phrase or "last" in phrase):
			cmd['A'] = "prev"
		elif("play" in phrase):
			cmd['B'] = phrase
		elif("by" in phrase):
			keywords = phrase.replace("play ","").split("by")
			cmd['B'] = keywords
		elif("play" in phrase and "playlist" in phrase):
			keywords = phrase.split("play ")[-1]
			cmd['B'] = keywords
		else:
			asay("No command received")
			return None
		if(len(cmd) >= 1):
			asay("Sending request to Spotify")
			ret = self.sendRequest(cmd)
		else:
			ret = None
		return ret


	#@classmethod
	def sendRequest(self, command):
		'''
			Sends appropriate request to Spotify
			@param command: parsed command dict (key = ['A','B','C']) 
		'''
		if(len(command) == 0):
			asay("Error: Command was empty")
			return
		key = command.keys()[0]
		cmd = command[key]
		asay("key: %s\t command: %s"%(key, str(cmd)))
		if(key == 'A'):
			if(cmd == "play"):
				sp_client.unpause(self._SP_OAUTH_TOKEN, self._SP_CSRF_TOKEN)
				asay(">> Play")
			elif("pause" in cmd or "does" in cmd):
				sp_client.pause(self._SP_OAUTH_TOKEN, self._SP_CSRF_TOKEN)
				asay("|| Paused")
			elif("skip" in cmd or "next" in cmd):
				if(len(self._TRACK_LIST) == 0):
					asay("Empty track list! Play a song to populate tracklist")
					return 
				track_number = random.randint(0, len(self._TRACK_LIST)-1)
				asay("Playing track number " + str(track_number))
				sp_client.play(self._SP_OAUTH_TOKEN, self._SP_CSRF_TOKEN, self._TRACK_LIST[track_number])

		elif(key == 'B'):
			# Play playlist
			if("playlist" in cmd):
				req_playlist = cmd.split("playlist ")[-1]
				playlist_uri = self._SP_PLAYLIST_DICT[req_playlist]['uri']
				playlist_id = self._SP_PLAYLIST_DICT[req_playlist]['id']
				if(playlist_uri == '0'):
					asay("Couldn't find playlist " + req_playlist)
					return False
				else:
					sp_client.play(self._SP_OAUTH_TOKEN, self._SP_CSRF_TOKEN, playlist_uri)
					playlist_tracks = self._SP.user_playlist_tracks(user=self._SP_USER, playlist_id=playlist_id)
					self._TRACK_LIST = [item['track']['uri'] for item in playlist_tracks['items']]
			# Play single track
			else:
				# Artist name only
				if("artist" in cmd):
					artist = cmd.split("artist")[-1]
					asay("Looking for " + str(artist))
					result = self._SP.search(q=artist, type='artist', limit=self._SP_TLIMIT)
					if(not result):
						asay("Couldn't find artist " + artist)
						return False
					asay("Playing " + str(result['artists']['items'][0]['name']))
					artist_uri = result['artists']['items'][0]['uri']
					sp_client.play(self._SP_OAUTH_TOKEN, self._SP_CSRF_TOKEN, artist_uri)
					# TODO Get remaining tracks in album to enable skipping

					return True
				# Track + Artist name provided
				elif("by" in cmd):
					cmd = cmd.replace("play ","")
					track, artist = cmd.split("by")
					asay("Looking for " + str(artist) + ":" + str(track))
					result = self._SP.search(q=track+" "+artist, type='track', limit=self._SP_TLIMIT)
				# Track name only
				else:
					track = cmd[0]
					asay("Looking for " + str(track))
					result = self._SP.search(q=track, type='track', limit=self._SP_TLIMIT)
				try:
					track_uri = result['tracks']['items'][0]['uri']				
					sp_client.play(self._SP_OAUTH_TOKEN, self._SP_CSRF_TOKEN, track_uri)
					album_uri = result['tracks']['items'][0]['album']['uri']
					album_tracks = self._SP.album_tracks(album_id=album_uri)
					self._TRACK_LIST = [item['uri'] for item in album_tracks['items']]
					# Single record? (one song in the album): search the artist playlist
					if(len(self._TRACK_LIST) <= 1):
						artist = result['tracks']['items'][0]['artists'][0]
						singles = self._SP.artist_albums(artist['id'])
						self._TRACK_LIST = []
						self._TRACK_LIST = [item['uri'] for item in singles['items']]
					return True
				except KeyError or IndexError:
					asay("Couldn't find URI")
					return False	