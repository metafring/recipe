import openai
import streamlit as st
from PIL import Image

from supabase import create_client


@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

st.markdown(
    """
<style>
footer {
    visibility: hidden;
}
</style>
""",
    unsafe_allow_html=True,
)

supabase_client = init_connection()

openai.api_key = st.secrets.OPENAI_TOKEN
openai_model_version = "gpt-3.5-turbo-0613"

css = """
    <style>
        @keyframes flame {
            0% { text-shadow: 0 0 10px #ff0000; }
            25% { text-shadow: 0 0 20px #ff5500; }
            50% { text-shadow: 0 0 30px #ffaa00; }
            75% { text-shadow: 0 0 20px #ff5500; }
            100% { text-shadow: 0 0 10px #ff0000; }
        }

        .title {
            font-size: 48px;
            font-weight : bold;
            text-align: center;
            font-weight: bold;
            animation: flame 2s infinite;
        }

        .title:hover{
            text-shadow:
                0 0 20px #ff0000,
                0 0 30px #ff5500,
                0 0 40px #ffaa00,
                0 0 50px #ffff00,
                0 0 60px #aaff00;
        }
    </style>
"""

st.markdown(css, unsafe_allow_html=True)
st.markdown("<p class='title'>백종원 레시피!</p>", unsafe_allow_html=True)
image = Image.open('../img/qor1.jpg')
image2 = Image.open('../img/qor2.png')

# 오디오 파일 재생
audio_file = open('../img/back.mp3', 'rb')
audio_bytes = audio_file.read()

st.image(image)
st.audio(audio_bytes, format='audio/mp3', start_time=0)
st.subheader("백종원에게 레시피를 물어보세요!")
st.text(f"Powerd by {openai_model_version}")

def generate_prompt(name):
    prompt = f""" 
    첫문장은 "안녕하세요! 백종원입니다!"로 시작해야 합니다.
{name}에 대한 요리 레시피를 알려 주세요.
대한민국 요식업 사업가인 백종원의 레시피로 알려줘야 합니다.
순서 대로 index 목차를 만들며 알려 줘야 합니다.
백종원 말투로 작성해 주세요. 
백종원 말투 중에 아래 사항은 필수입니다.
문장 마지막에 '지요' 혹은 '죠'가 들어가야 할 때 이를 '쥬'로 바꿔야 합니다. (예를 들어 '볶아주면 되죠?'가 아니라 '볶아주면 되쥬?'로 해야 함. '맛있죠?'가 아니라 '맛있쥬?'.)
---
요리 이름: {name}
---
"""
    return prompt.strip()


def request_chat_completion(prompt):
    response = openai.ChatCompletion.create(
        model=openai_model_version,
        messages=[
            {"role": "system", "content": "당신은 전문 카피라이터입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]

def write_prompt_result(prompt, result):
    response = supabase_client.table("prompt_result").insert(
        {
            "prompt":name,
            "result":result
        }
    ).execute()
    print(response)

with st.form("form"):
    name = st.text_input("하고 싶은 요리")
    submitted = st.form_submit_button("Submit")
    if submitted:
        if not name:
            st.error("요리의 이름을 입력해주세요")
        else:
            with st.spinner('백종원이 생각 중 입니다...'):
                st.image(image2)
                prompt = generate_prompt(name)
                response = request_chat_completion(prompt)
                write_prompt_result(prompt, response)
                st.text_area(
                    label="백종원이 대답합니다.",
                    value=response,
                    placeholder="아직 생성된 문구가 없습니다.",
                    height=500
                )
