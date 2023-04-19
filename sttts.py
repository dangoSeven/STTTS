import pyaudio
import wave
import numpy as np
import os
import requests
import json
import pygame
import re
import threading
import queue
import dotenv
import soundfile as sf
import sys
import signal

from collections import defaultdict
from faster_whisper import WhisperModel

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "audio_{0}.wav"
SILENCE_THRESHOLD = 1000
SILENCE_CHUNKS = 20

dotenv.load_dotenv()
api_key = str(os.getenv('ELEVEN_LABS_API_KEY'))
voice_id = str(os.getenv('VOICE_ID'))
stability = os.getenv('STABILITY')
similarity_boost = os.getenv('SIMILARITY_BOOST')
vad = int(os.getenv('VAD'))

played_files = defaultdict(lambda: False)

# Load the faster-whisper model
model = WhisperModel("small", device="cuda", compute_type="float16")

file_queue = queue.Queue()

exit_app = False

def play_audio(filename):
    reduced_sample_rate = 44100  # Lower sample rate (default: 44100)
    reduced_bit_depth = -16       # Lower bit depth (default: -16)

    pygame.mixer.init(frequency=reduced_sample_rate, size=reduced_bit_depth)
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.quit()

def save_audio(filename, recording, samplerate=44100):
    data = np.array(recording * (2**15 - 1), dtype=np.int16)
    sf.write(filename, data, samplerate)

def speech_to_text(filename):
    data_file_path = os.path.join(os.path.dirname(sys.argv[0]), filename)
    if vad < 1:
        segments, _ = model.transcribe(data_file_path, beam_size=5)
    else:
        segments, _ = model.transcribe(data_file_path, vad_filter=True)
    text_result = ' '.join([segment.text for segment in segments])
    print(text_result)

    if "exit app" in text_result.lower():
        quit()
    if (re.sub(r'\W+', '', text_result).isalnum() and text_result.isascii()):
        text_to_speech(text_result)

def text_to_speech(text):
    global api_key, voice_id, stability, similarity_boost

    voice_settings = {"stability": stability, "similarity_boost": similarity_boost}

    headers = {
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }

    data = {
        "text": text,
        "voice_settings": voice_settings,
    }

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers=headers,
        data=json.dumps(data),
    )

    if response.status_code == 200:
        with open("output.mp3", "wb") as output_file:
            output_file.write(response.content)
        print("Text-to-speech conversion successful. Audio saved as output.mp3")
        play_audio("output.mp3")
    else:
        print("Error:", response.status_code, response.text)

def is_silent(data, threshold=SILENCE_THRESHOLD):
    return np.mean(np.abs(data)) < threshold


def process_audio_files():
    played_files = {}
    while True and exit_app == False:
        if not file_queue.empty():
            filename = file_queue.get()
            played_files[filename] = False
            speech_to_text(filename)
            played_files[filename] = True

fileCount = 0

def record_audio():
    global fileCount
    global exit_app
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

    print("Waiting for you to start talking...")

    while True and exit_app == False:
        data = stream.read(CHUNK)
        data_np = np.frombuffer(data, dtype=np.int16)
        if not is_silent(data_np):
            print("Recording started!")
            break

    print("Recording...")
    frames = [data]
    silent_chunks = 0
    recorded_chunks = 0

    while True and exit_app == False:
        data = stream.read(CHUNK)
        data_np = np.frombuffer(data, dtype=np.int16)
        frames.append(data)
        recorded_chunks += 1

        if is_silent(data_np):
            silent_chunks += 1
            if silent_chunks >= SILENCE_CHUNKS:
                break
        else:
            silent_chunks = 0

    stream.stop_stream()
    stream.close()
    p.terminate()

    if recorded_chunks > (RATE // CHUNK) // 3:  # Check if the recording duration is longer than 1 second
        print("Finished recording")
        # Find a played file to overwrite
        if fileCount > 4:
            fileCount = 0
            filename = WAVE_OUTPUT_FILENAME.format(fileCount)
        else:
            # If no played file is found, create a new one
            filename = WAVE_OUTPUT_FILENAME.format(fileCount)

        with wave.open(filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))

        file_queue.put(filename)  # Add the file to the queue
        fileCount = fileCount + 1
    else:
        print("Recording too short, not saving.")

def exit_handler(signal, frame):
    global exit_app
    print("\nExiting gracefully...")
    exit_app = True
    # Release any resources here
    pygame.mixer.quit()
    sys.exit(0)

if __name__ == "__main__":

    # Register the exit handler for KeyboardInterrupt (Ctrl+C)
    signal.signal(signal.SIGINT, exit_handler)

    processing_thread = threading.Thread(target=process_audio_files)
    processing_thread.start()

    while True:
            try:
                record_audio()
            except KeyboardInterrupt:
                exit_handler(None, None)
