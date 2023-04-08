# STTTS
## Description

A speech to text to speech script developed almost entirely using ChatGPT. Part of a series of scripts/apps that I'm building using ChatGPT.

## Requirements

- I'm using Python 3.10.10 for this.

- You need FFMPEG installed on your machine and added to your system PATH.

## Setup

- Rename env_sample to .env

- Edit the .env with notepad or some text editor

- Replace 'your api key here' with your Eleven Labs API Key. Keep the single quotes.

- Do the same with the Voice ID. This is the ID of the voice that you will be using. Keep the single quotes.

- When you run start.bat you'll see a list of all your voices and their IDs. Or you can use this API call from the Eleven Labs website: https://api.elevenlabs.io/docs#/voices/Get_voices_v1_voices_get

## Usage

- The first time you run start.bat, it will take some time for Whisper to install the Speech to text model and for pip to install all the python requirements, give it a minute while it does its thing.

- Once you see "Waiting for you to start talking..." in the console, you are ready to go.

- The first sentence that you run through the app takes longer, probably due to some initialization or something. Afterwards there should only be a 1-4 second delay for the translation.

- To close the application, say "Exit App" to gracefully kill the process then just close the console or spam crtl+c on the console.

- If you want the voice to come out of your microphone in a game, you'll have to use something like VoiceMeeter to capture the outputted voice and pass it to your games mic/input. I will provide instructions on how to do this in the future.

## Disclaimer
- 99% of this code came from ChatGPT. You're welcome to go through the included python files to see how all this works. Feel free to Fork this to improve upon it.
- If you're using this for your stream or something, give me a little shouout sometime :)