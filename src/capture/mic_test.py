import speech_recognition as sr

# Obtain audio from the microphone
r = sr.Recognizer()
with sr.Microphone() as source:
	print("Say something!")
	audio = r.listen(source, phrase_time_limit=5)


# Recognize using wit.ai
WIT_AI_KEY = "GP3LO2LIQ2Y4OSKOXZN6OAOONB55ZLN5"
try:
	print("wit.ai thinks you said " + r.recognize_wit(audio, key=WIT_AI_KEY))
except sr.UnknownValueError:
	print("wit.ai could not understand audio")
except sr.RequestError as e:
	print("Could not request results from wit.ai servicel {0}".format(e))
	