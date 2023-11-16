import openai
import listentomic

def record_and_transcribe(duration=5, sample_rate=16000):
    print('Transcribing...')
    filename = '/tmp/gptexecsound.wav'
    listentomic.detect_silence_and_save(output_file=filename)
    
    client = openai.OpenAI()
    with open(filename, 'rb') as audio_data:
        transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_data)
    return transcription.text

# Example usage
if __name__ == '__main__':
    transcribed_text = record_and_transcribe()
    print('Transcribed text:')
    print(transcribed_text)
