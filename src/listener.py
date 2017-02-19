'''
	@project: Atlas
	@file: listener.py
	@objective: receives audio and converts to text commands
	@author: Amlan Nayak

	Extended from uberi/speech_recognition example
'''
import speech_recognition as sr
import sys, time
import spotipy

WIT_AI_KEY = "GP3LO2LIQ2Y4OSKOXZN6OAOONB55ZLN5"

def asay(msg):
	print("@apollo: " + msg)
def usay(msg):
	print("@me: " + msg)

class captured_audio:
	def __init__(self, timeout=None, ptl=None):
		# Which online recognizer to use
		self.recognizer = "wit"
		self.timeout = timeout
		# phrase_time_limit
		self.ptl = ptl
		# captured command returned by recognizer
		self.command = ""

	def callback(recog, audio):
		'''
			Listener thread calls this when a phrase is detected
			Saves response in self.command variable
			@param recog: recognizer object
			@param audio: phrase captured from device
		'''
		asay("I heard something!")
		try:
			self.command = recog.recognize_wit(audio, key=WIT_AI_KEY))
			usay(self.command)
		except sr.UnknownValueError:
			print("Wit.ai could not understand audio")
		except sr.RequestError as e:
			print("Could not request results from Wit.ai service; {0}".format(e))

class command:
	@TODO
	def __init__(self):
		self.commands = []
		self.curr = []

	def parse(phrase):
		'''
			Parses transcribed phrase into command keywords
			Currently supports:
				- "Play <song> by <artist>"
				- "Play/Pause"
				- "Add this song to playlist <playlist>"
				- "Skip this song"
				- "Play previous song"
			@param phrase: transcribed phrase received from
				captured_audio instance
		'''
		# Play command
		if phrase.lower().strip(" ") == "play":
			self.cmd = ["play"]
		# Pause command
		elif phrase.lower().strip(" ") == "pause":
			self.cmd = ["pause"]
		# Play <song> by <artist>
		elif "by" in phrase.lower():
			song = phrase.split("by")[0]
			artist = phrase.split("by")[-1]
			self.cmd = [song, artist]
			self.curr.pop()
			self.curr.append()
		# Add song to playlist
		elif "playlist" in phrase.lower():
			if("add" in phrase.lower()):
				self.cmd = ["add", ]



def main():
	'''
		Main listening loop (runs until explicitly killed)
	'''
	r = sr.Recognizer()
	m = sr.Microphone()

	# Adjusting to ambient noise level
	asay("Hi! I'm Apollo!")
	with m as source:
		asay("Let me adjust the mic really quick")
		r.adjust_for_ambient_noise(source)

	# Instantiating captured_audio instance
	aud_inst = captured_audio(ptl=6)
 	stop_listening = r.listen_in_background(m, aud_inst.callback)
 	
 	# Busy loop while background thread listens
 	asay("... waiting for command ...")
	while True:
		time.sleep(0.1) # we're still listening even though the main thread is doing other things

if __name__ == "__main__":
	main()
