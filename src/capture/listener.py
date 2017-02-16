''' @project: Atlas
	@file: listener.py
	@objective: receives audio and converts to text commands
	@author: Amlan Nayak 

	Extended from uberi/speech_recognition example
'''
import speech_recognition as sr 
import sys

WIT_AI_KEY = "" 

# Get audio from mic
r = sr.recognizer()
r.energy_threshold = 4000


# Called from background thread
def callback(recog, audio):
	# use wit.ai to recognize audio data
	try:


