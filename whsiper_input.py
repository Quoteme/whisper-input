import whisper
import pyaudio
import wave
import pyautogui
import audioop
import time
from plyer import notification
import argparse
from termcolor import colored
import tempfile
import os
import beepy

def play_beep(sound_type, beep_enabled):
    if beep_enabled:
        beepy.beep(sound_type)

def record_speech(silence_threshold=500, silence_duration=10, beep_enabled=True):
    notification.notify(title="Speech-to-Text", message="Start Speaking...", app_name="Speech-to-Text")
    
    # Initialize PyAudio and Recorder
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    frames = []
    last_sound_time = time.time()

    while True:
        data = stream.read(1024)
        frames.append(data)

        # Check volume
        rms = audioop.rms(data, 2)
        if rms > silence_threshold:
            last_sound_time = time.time()

        # Check if silence duration is reached
        if (time.time() - last_sound_time) > silence_duration:
            break

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Create a temporary file to save the recording
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, "recording.wav")
    wf = wave.open(temp_file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()

    return temp_file_path

def transcribe_speech(file_path, beep_enabled=True):
    notification.notify(title="Speech-to-Text", message="Processing recording...", app_name="Speech-to-Text")
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    return result["text"]

def type_text(text):
    pyautogui.write(text)

# Argument parsing
parser = argparse.ArgumentParser(description="Speech-to-Text with Silence Threshold")
parser.add_argument("--silence_duration", type=int, default=5, help="Duration of silence before stopping recording (in seconds)")
parser.add_argument("--beep", action='store_true', help="Enable beep sound at start and end")
args = parser.parse_args()

if args.silence_duration == 5:
    print(colored('No silence duration argument provided, using default value of 5 seconds.', 'yellow'))
    print(colored('Example usage: python script_name.py --silence_duration 1 --beep', 'green'))

# Step 1: Play start beep
play_beep(sound_type=1, beep_enabled=args.beep)

# Step 2 and 3: Record and transcribe speech
speech_file = record_speech(silence_duration=args.silence_duration, beep_enabled=args.beep)
transcribed_text = transcribe_speech(speech_file, beep_enabled=args.beep)

# Step 4: Type the text
type_text(transcribed_text)

# Step 5: Play end beep and show notification
play_beep(sound_type=1, beep_enabled=args.beep)
notification.notify(title="Speech-to-Text", message="Transcription complete!", app_name="Speech-to-Text")

