'''
	@project: Atlas
	@file: listener.py
	@objective: receives audio and converts to text commands
	@author: Amlan Nayak

	Extended from uberi/speech_recognition example
'''
import speech_recognition as sr
import sys, time

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
			usay(recog.recognize_wit(audio, key=WIT_AI_KEY))
		except sr.UnknownValueError:
			print("Wit.ai could not understand audio")
		except sr.RequestError as e:
			print("Could not request results from Wit.ai service; {0}".format(e))


def main():
	r = sr.Recognizer()
	m = sr.Microphone()

	asay("Hi! I'm Apollo!")
	with m as source:
		asay("Let me adjust the mic really quick")
		r.adjust_for_ambient_noise(source)

 	stop_listening = r.listen_in_background(m, callback)
 	
 	# do some other computation for 5 seconds, then stop listening and keep doing other computations
	while True:
		time.sleep(0.1) # we're still listening even though the main thread is doing other things
	stop_listening() # calling this function requests that the background listener stop listening
	asay("I'm done for now.")
	while True: 
		time.sleep(0.1)

if __name__ == "__main__":
	main()
