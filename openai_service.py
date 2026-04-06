from openai import OpenAI
from dotenv import load_dotenv
import os
import base64

load_dotenv()
# print(os.environ['OPENAI_API_KEY'])
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=OPENAI_API_KEY)

def stt(audio):

    #파일로 변환
    output_filename = 'input.mp3'
    audio.export(output_filename, format='mp3')

    with open('input.mp3', 'rb') as f:
        transcription = client.audio.transcriptions.create(
            model='whisper-1',
            file=f,
            language='ko'
        )
        # print(transcription.text)

    # 음원파일 삭제
    os.remove('input.mp3')
    return transcription.text

def ask_gpt(messages, model):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=1,
        top_p=1,
        max_completion_tokens=4096
    )
    return response.choices[0].message.content

def tts(response: str):
    filename = 'output.mp3'
    with client.audio.speech.with_streaming_response.create(
        model='tts-1',
        voice='nova',
        input=response
    ) as rest:
        rest.stream_to_file(filename)

    # 음원을 base64문자열로 인코딩 처리
    with open('output.mp3', 'rb') as f:
        data = f.read()
        base64_encoded = base64.b64encode(data).decode() # 이진데이터 -> base64인코딩(이진) -> 문자열로 디코딩

    os.remove(filename)
    return base64_encoded
