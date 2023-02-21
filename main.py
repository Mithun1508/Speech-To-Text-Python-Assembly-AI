import requests
import time
import os


API_KEY = os.getenv("API_KEY")

upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'

headers_auth_only = {'authorization': API_KEY}

headers = {
    "authorization": API_KEY,
    "content-type": "application/json"
}

CHUNK_SIZE = 5_242_880  # 5MB


def upload(filename):
    print(f"Step 1: Uploading file '{filename}'...", end="")
    def read_file(filename):
        with open(filename, 'rb') as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                yield data

    upload_response = requests.post(upload_endpoint,
                                    data=read_file(filename),
                                    headers=headers_auth_only)
    print(f'Uploading done')
    return upload_response.json()['upload_url']


def transcribe(audio_url):
    print('Step 2: Start Transcription...')
    transcript_request = {
        'audio_url': audio_url
    }

    transcript_response = requests.post(transcript_endpoint,
                                        json=transcript_request,
                                        headers=headers)
    return transcript_response.json()['id']

        
def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers)
    return polling_response.json()


def get_transcription_result(audio_url):
    transcribe_id = transcribe(audio_url)
    print('Step 3: Waiting for transcription result...')
    while True:
        data = poll(transcribe_id)
        if data['status'] == 'completed':
            print('Transcription completed 😊')
            return data, None
        elif data['status'] == 'error':
            return data, data['error']
            
        print("Waiting for 5 more seconds...")
        time.sleep(5)
        

def main(filename):    
    audio_url = upload(filename)

    data, error = get_transcription_result(audio_url)
    if data:
        transcript = data['text']
        print(f'\nTranscript:\n\n{transcript}')
    elif error:
        print("Error!!!", error)


if __name__ == '__main__':
    if API_KEY is None:
        print('Could not find an environment variable named API_KEY.\n\nYou can create one for free at https://www.assemblyai.com')
    else:
        print("Found API_KEY. Let's go!\n")
        main(filename="example-audio.m4a")