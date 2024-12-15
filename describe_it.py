import streamlit as st
import openai
from PIL import Image
import random
import os
import time
import re
import json

# OpenAI API 설정
openai_api_key = st.secrets["openai"]["api_key"]
openai.api_key = openai_api_key

# 준비된 이미지와 정답 문장 데이터 및 힌트 데이터
images = [
    {
        "image": "image1.jpg", 
        "answer": "The boy who became a male dancer plays ballet in an academy full of female dancers.",
        "keywords": ["boy", "academy", "female"],
        "grammar_hint": "관계대명사 who 사용한 주어를 가지고 있어."
    },
    {
        "image": "image2.jpg", 
        "answer": "A Jewish boy is eating bread with his friend's permission while working at home as a Nazi officer.",
        "keywords": ["Jewish", "eat", "bread"],
        "grammar_hint": "'~하면서' 의미를 가지는 접속사 while을 사용해보아."
    },
    {
        "image": "image3.jpg", 
        "answer": "There is a lot of water in the bathroom, so a bathtub with a brown bear in a red hat flows down the stairs with the water.",
        "keywords": ["water", "bathtub", "stairs"],
        "grammar_hint": "there 구문을 사용할 수 있어, so를 이용해 두 문장을 연결해주어."
    },
    {
        "image": "image4.jpg", 
        "answer": "A man who is holding a blue book and a woman are smiling under the London Clock Tower, facing each other.",
        "keywords": ["hold", "smile", "face"],
        "grammar_hint": "관계대명사 who 사용한 주어를 가지고 있고, 분사구문을 사용해보아."
    },
    {
        "image": "image5.jpg", 
        "answer": "At night a big boat is leaning upward because it hits an iceberg in the middle of the sea.",
        "keywords": ["boat", "lean", "iceberg"],
        "grammar_hint": "이유를 나타내는 접속사 because를 사용하고 현재 진행형을 사용해보아."
    }
]

# 세션 상태 초기화 함수
def initialize_session_state():
    if "current_round" not in st.session_state:
        st.session_state.current_round = 0
    if "hint_words" not in st.session_state:
        st.session_state.hint_words = ""
    if "grammar_hint" not in st.session_state:
        st.session_state.grammar_hint = ""
    if "generated_image_url" not in st.session_state:
        st.session_state.generated_image_url = None
    if "selected_images" not in st.session_state:
        st.session_state.selected_images = random.sample(images, 3)
    if "responses" not in st.session_state:
        st.session_state.responses = []

initialize_session_state()

# 상태 초기화 함수
def reset_state():
    st.session_state.hint_words = ""
    st.session_state.grammar_hint = ""
    st.session_state.generated_image_url = None

# JSON 저장 함수
def save_to_json():
    folder_path = "./pages"
    os.makedirs(folder_path, exist_ok=True)
    for idx, response in enumerate(st.session_state.responses, start=1):
        file_path = os.path.join(folder_path, f"problem_{idx}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(response, f, ensure_ascii=False, indent=4)

# 문제 화면 렌더링 함수
def render_quiz_page():
    if st.session_state.current_round < 3:
        st.markdown("<h1 style='text-align: center; font-weight: bold;'>Describe IT!!!</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{st.session_state.current_round + 1}번째 문제: 문장을 작성하세요</h2>", unsafe_allow_html=True)

        selected_image = st.session_state.selected_images[st.session_state.current_round]

        # 이미지 표시
        col1, col2 = st.columns([1, 1])
        with col1:
            if os.path.exists(selected_image["image"]):
                st.image(selected_image["image"], caption="문제 이미지", use_container_width=True)
            else:
                st.warning("이미지 파일을 찾을 수 없습니다.")

        # 문장 입력창
        placeholder_text = "영어 프롬프트를 입력하고 아래 [이미지 생성] 버튼을 눌러 주세요. [단어 힌트]와 [구문 힌트]를 참고할 수 있습니다. 영어 프롬프트를 완성하면 [다음 문제로] 버튼을 눌러 주세요. 문제는 총 3문제 입니다."
        student_sentence = st.text_area("영어로 문장을 입력하세요:", placeholder=placeholder_text, key=f"student_sentence_{st.session_state.current_round}")

        # 입력값 검증
        is_english = re.match(r'^[a-zA-Z0-9\s.,?!]+$', student_sentence)
        if student_sentence and not is_english:
            st.error("Only English")

        # 이미지 생성 버튼
        if st.button("이미지 생성", key=f"generate_image_{st.session_state.current_round}"):
            if student_sentence and is_english:
                with st.spinner("이미지 생성 중..."):
                    time.sleep(2)  # 이미지 생성 시간을 시뮬레이션
                    try:
                        response = openai.Image.create(
                            prompt=student_sentence,
                            n=1,
                            size="512x512"
                        )
                        st.session_state.generated_image_url = response['data'][0]['url']
                    except Exception as e:
                        st.error(f"이미지 생성 오류: {e}")

        with col2:
            if st.session_state.generated_image_url:
                st.image(st.session_state.generated_image_url, caption="생성된 이미지", use_container_width=True)

        # 힌트 제공
        col_hint1, col_hint2 = st.columns(2)
        with col_hint1:
            if st.button("단어 힌트", key=f"hint_words_{st.session_state.current_round}"):
                st.session_state.hint_words = ', '.join(selected_image["keywords"])
        with col_hint2:
            if st.session_state.hint_words:
                st.info(f" : {st.session_state.hint_words}")

        col_grammar1, col_grammar2 = st.columns(2)
        with col_grammar1:
            if st.button("구문 힌트", key=f"grammar_hint_{st.session_state.current_round}"):
                st.session_state.grammar_hint = selected_image["grammar_hint"]
        with col_grammar2:
            if st.session_state.grammar_hint:
                st.info(f" : {st.session_state.grammar_hint}")

        # 다음 문제로 버튼
        if st.session_state.current_round < 2:
            if st.button("다음 문제로", key=f"next_question_{st.session_state.current_round}"):
                st.session_state.responses.append({
                    "image": selected_image["image"],
                    "student_sentence": student_sentence,
                    "correct_answer": selected_image["answer"]
                })
                st.session_state.current_round += 1
                reset_state()
        else:
            if st.button("제출 후 피드백 받기"):
                st.session_state.responses.append({
                    "image": selected_image["image"],
                    "student_sentence": student_sentence,
                    "correct_answer": selected_image["answer"]
                })
                save_to_json()
                st.switch_page('pages/feedback.py')
              
# 메인 로직
if st.session_state.current_round < 3:
    render_quiz_page()
else:
    save_to_json()
    st.switch_page('pages/feedback.py')
