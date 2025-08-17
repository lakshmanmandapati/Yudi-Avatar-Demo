from gtts import gTTS
from pydub import AudioSegment

# Text to speech
text = "Hello, this is a test order for one coffee."
tts = gTTS(text=text, lang="en")

# Save as mp3
tts.save("sample.mp3")

# Convert mp3 → wav
sound = AudioSegment.from_mp3("sample.mp3")
sound.export("sample.wav", format="wav")

print("✅ Generated sample.wav")
