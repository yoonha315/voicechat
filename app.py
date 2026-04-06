import streamlit as st
from audiorecorder import audiorecorder
from openai_service import stt, ask_gpt, tts

def main():
    st.set_page_config(
        page_title='😎Voice Chatbot😎',
        page_icon="🎤",
        layout='wide'
    )
    st.header('🎤Voice Chatbot🎤')
    st.markdown('---')

    with st.expander('Voice Chatbot 프로그램 처리절차', expanded=False):
        st.write(
            """  
            1. 녹음하기 버튼을 눌러 질문을 녹음합니다.  
            2. 녹음이 완료되면 자동으로 Whisper모델을 이용해 음성을 텍스트로 변환합니다.   
3. 변환된 텍스트로 LLM에 질의후 응답을 받습니다.  
            4. LLM의 응답을 다시 TTS모델을 사용해 음성으로 변환하고 이를 사용자에게 들려줍니다.  
            5. 모든 질문/답변은 채팅형식의 텍스트로 제공합니다.  
            """)

    # session_state 초기화
    system_prompt = (
        '당신은 친절한 챗봇입니다. 사용자의 질문에 50단어 이내로 간결하게 답변해주세요.'
        '사용자가 다른 언어로 말하거나 질문이 다른 언어로 인식되더라도, 답변은 항상 한국어로만 작성합니다.'
    )
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [
            {'role': 'system', 'content': system_prompt}
        ]
    if 'check_reset' not in st.session_state:
        st.session_state['check_reset'] = False

    with st.sidebar:
        model = st.radio(label='GPT 모델', options=['gpt-4.1', 'gpt-5-nano', 'gpt-5.2'], index=2)
        print(f'model={model}')

        if st.button(label='초기화'):
            st.session_state['check_reset'] = True

            # 내용 초기화
            st.session_state['messages'] = [
                {'role': 'system', 'content': system_prompt}
            ]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('녹음하기')
        audio = audiorecorder()
        # print(audio)
        # print(audio.duration_seconds)

        # 녹음한 시간이 존재하고, 리셋 버튼을 누르지 않았을 때
        if((audio.duration_seconds > 0) and (not st.session_state['check_reset'])):
            st.audio(audio.export().read()) # audiorecored로 녹음된 내용을 읽어서 audio 재생기를 화면에 출력

            # 1. stt 변환
            query: str = stt(audio)
            print(f'{query = }')

            # 2. llm 질의
            st.session_state['messages'].append({'role':'user', 'content': query})
            response: str = ask_gpt(st.session_state['messages'], model)
            print(f'{response = }')
            st.session_state['messages'].append({'role':'assistant', 'content': response})
            print(st.session_state['messages'])

            # 3. tts 변환(base64문자열 형태로 반환할 예정)
            base64_encoded_audio: str = tts(response)

            st.html(f'''
            <audio autoplay='true'>
                <source src='data:audio/mp3;base64, {base64_encoded_audio}' type='audio/mp3'/>
            </audio>
            ''')

        else:
            st.session_state['check_reset'] = False  # 처음 check_reset 상태로 돌려 놓기

    with col2:
        st.subheader('질문/답변')
        if ((audio.duration_seconds > 0) and (not st.session_state['check_reset'])):
            for message in st.session_state['messages']:
                role = message['role']
                content = message['content']

                if role =='system':
                    continue

                with st.chat_message(role):
                    st.markdown(content)
        else:
            st.session_state['check_reset'] = False  # 처음 check_reset 상태로 돌려 놓기

if __name__ == '__main__':
    main()
