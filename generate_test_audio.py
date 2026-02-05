import wave
import math
import struct
import os

def generate_sine_wave(frequency, duration, sample_rate=44100, volume=0.5):
    num_samples = int(duration * sample_rate)
    audio = []
    for i in range(num_samples):
        # Generate sine wave
        value = int(volume * 32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
        audio.append(value)
    return audio

def save_wav(filename, audio, sample_rate=44100):
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit PCM)
        wav_file.setframerate(sample_rate)
        for sample in audio:
            wav_file.writeframes(struct.pack('<h', sample))

if __name__ == "__main__":
    output_path = os.path.join("assets", "music", "test_beep.wav")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print("Generating test audio...")
    audio_data = generate_sine_wave(frequency=440, duration=5.0) # 5 seconds of A4 note
    save_wav(output_path, audio_data)
    print(f"Saved to {output_path}")
