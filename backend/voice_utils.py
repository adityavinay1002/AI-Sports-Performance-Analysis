import os
import speech_recognition as sr
from pydub import AudioSegment

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes audio file to text using SpeechRecognition.
    Supports common web audio formats.
    """
    if not os.path.exists(audio_path):
        return f"Error: Audio file not found at {audio_path}"

    try:
        # Check if conversion to WAV is needed
        base, ext = os.path.splitext(audio_path)
        wav_path = f"{base}_converted.wav"
        
        # Load audio using pydub
        if ext.lower() == '.webm':
            audio = AudioSegment.from_file(audio_path, format="webm")
            audio.export(wav_path, format="wav")
        elif ext.lower() == '.wav':
            wav_path = audio_path # Already WAV
        else:
            # Try generic conversion
            audio = AudioSegment.from_file(audio_path)
            audio.export(wav_path, format="wav")

        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data) # Using Google's free STT
            
        # Clean up temporary WAV if created
        if wav_path != audio_path and os.path.exists(wav_path):
            os.remove(wav_path)
            
        return text.strip()
    except sr.UnknownValueError:
        return "Could not understand the audio. Please try again."
    except sr.RequestError as e:
        return f"Error with the speech recognition service: {e}"
    except Exception as e:
        print(f"Transcription error: {e}")
        return f"Error transcribing audio: {str(e)}"

# Example usage for testing
if __name__ == "__main__":
    # This would require an actual audio file to test
    print(transcribe_audio("test_sample.webm"))
