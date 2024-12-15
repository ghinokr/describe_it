import streamlit as st
import json
import os
import matplotlib.pyplot as plt
import openai
import matplotlib
import re

# 한글 포트 설정
matplotlib.rc('font', family='Malgun Gothic')

# JSON 파일 로드 함수
def load_json_data():
    folder_path = "./pages"
    data = []
    for i in range(1, 4):  # 1~3번 문제
        file_path = os.path.join(folder_path, f"problem_{i}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data.append(json.load(f))
    return data

# 데이터 로드
responses = load_json_data()

# 평가 등급 리스트
grades = []

# 그래프 자리 확보
graph_placeholder = st.empty()

# 데이터가 없을 경우 경고 메시지 표시
if not responses:
    st.error("문제 데이터가 없습니다. JSON 파일을 확인하세요.")
else:
    # 각 문제에 대한 정보 표시
    for idx, response in enumerate(responses, start=1):
        st.subheader(f"문제 {idx}")

        # 4분할 레이아웃 생성
        col1, col2, col3, col4 = st.columns(4)

        # 이미지 표시
        with col1:
            image_path = response.get("image", "")
            if os.path.exists(image_path):
                st.image(image_path, caption=f"문제 {idx} 이미지", use_container_width=True)
            else:
                st.warning(f"문제 {idx}의 이미지를 찾을 수 없습니다.")

        # 학생의 답변 표시
        with col2:
            st.write("**학생의 답변:**")
            student_sentence = response.get("student_sentence", "답변 없음")
            st.write(student_sentence)

        # 정답 표시
        with col3:
            st.write("**정답:**")
            correct_answer = response.get("correct_answer", "정답 없음")
            st.write(correct_answer)

        # 피드백 표시
        with col4:
            if student_sentence == "답변 없음" or not student_sentence.strip():
                st.warning("학생의 답변이 입력되지 않았습니다.")
                grades.append("C")  # 기본 등급으로 처리
            else:
                comparison_prompt = f"""
                Student sentence: {student_sentence}
                Correct answer: {correct_answer}
                Provide the following feedback format in Korean:

                최종 평가 : [A or B or C]
                - 문법 평가 : 문법적 정확성과 관련된 코멘트
                - 내용 평가 : 내용과 관련된 피드백, 자연스러운 표현 제안
                - 기타 : 기타 필요한 수정 사항
                """
                try:
                    feedback_response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an English teacher evaluating student work. You should provide feedback strictly in the requested format in Korean. Make sure the grade is always A, B, or C."},
                            {"role": "user", "content": comparison_prompt}
                        ]
                    )
                    feedback = feedback_response['choices'][0]['message']['content']
                    #st.write("디버그용 피드백 출력:")
                    st.write(feedback)  # 디버그용 출력

                    # 등급 추출
                    match = re.search(r"최종 평가 *: *(A|B|C)", feedback)
                    if match:
                        grade = match.group(1)
                    else:
                        grade = "C"  # 기본 등급
                        st.warning("피드백에서 등급을 추출할 수 없어 기본 등급 'C'로 처리합니다.")

                    grades.append(grade)

                except Exception as e:
                    st.warning("피드백 생성 중 문제가 발생했습니다. 기본 등급 'C'로 처리합니다.")
                    grades.append("C")

    # 평가 결과 그래프 생성
    def display_feedback():
        if len(grades) == len(responses):
            with graph_placeholder.container():
                st.header(f"평가 결과 그래프 [{' - '.join(grades)}]")
                grade_to_score = {"C": 1, "B": 2, "A": 3}
                scores = [grade_to_score[grade] for grade in grades]
                plt.figure(figsize=(10, 5))
                plt.plot(range(1, len(scores) + 1), scores, marker='o', linestyle='-', color='b')
                plt.xticks(range(1, len(scores) + 1), labels=[str(i) for i in range(1, len(scores) + 1)])
                plt.yticks([1, 2, 3], labels=['C', 'B', 'A'])
                plt.xlabel('평가 차수 (1, 2, 3)')
                plt.ylabel('평가 등급 (C, B, A)')
                plt.title('학생의 평가 결과 변화')
                plt.ylim(0, 3)  # Y축 범위를 0-3으로 설정 (1, 2, 3만 사용)
                st.pyplot(plt)
        else:
            graph_placeholder.warning("평가 데이터가 일부 누락되었습니다. 모든 문제에 답변이 입력되었는지 확인하세요.")

    # 최종 평가 후 그래프 표시
display_feedback()
