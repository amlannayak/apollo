## Spotify Voice Controller

An extremely basic voice controller for the Spotify Desktop application using [Google Speech API](https://cloud.google.com/speech/) for command transcription. 

### Instructions 
**NOTE:** _This has only been tested on macOS_
Install [Spotify](https://www.spotify.com/us/) and start the application. A few environment variables need to be set in order to run the controller:
* The spotipy client ID and client Secret (you can obtain a pair for yourself)
* Google Speech Application credentials

The client class is defined in spvClient.py. An instance of this class is used as the interface between the Google Speech API and Spotify. It parses the text returned by Speech API and sends the corresponding commands to the Spotify application. Supported commands include:

- "Play 'Your Hand in Mine' by Explosions in the Sky"
- "Play artist "
- "Pause"
- "Skip this one"

More commands may/may not be added in the future

## Dependencies
Google Speech API
spotipy 
