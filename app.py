import streamlit as st
from PoseLandmarkerModule import PoseLandmarkerModule
from save_video import BellRecorder
import cv2

# Streamlit 앱 시작
st.title("우리 집 AI 경비원")

# 모델 및 동영상 경로 입력
model_path = st.text_input("Pose Landmarker 모델 경로", "pose_landmarker_full.task")
video_path = st.file_uploader("비디오 업로드", type=["mp4", "avi"])


region = {
        'x_min': 350,
        'x_max': 400,
        'y_min': 75,
        'y_max': 125
    }

# 이메일 정보 입력
st.sidebar.header("이메일 설정")
smtp_server = st.sidebar.text_input("SMTP 서버", "smtp.gmail.com")
smtp_port = st.sidebar.number_input("SMTP 포트", value=587)
username = st.sidebar.text_input("이메일 주소", "gnfmcm333@gmail.com")
password = st.sidebar.text_input("비밀번호", type="password")
to_email = st.sidebar.text_input("받는 이메일 주소", "gnfmcm333@gmail.com")

email_info = {
    "smtp_server": smtp_server,
    "smtp_port": smtp_port,
    "username": username,
    "password": password,
    "to_email": to_email
}

# 비디오 처리 버튼
if st.button("비디오 처리 시작"):
    if video_path:
        # 임시 파일 저장
        temp_video_path = "uploaded_video.mp4"
        with open(temp_video_path, "wb") as f:
            f.write(video_path.read())

        # Pose Landmarker 모듈 실행
        pose_landmarker = PoseLandmarkerModule(model_path, temp_video_path, region, email_info)
        captured_images = pose_landmarker.process_video()

        if captured_images:
            st.success(f"총 {len(captured_images)}개의 이미지를 캡처했습니다.")
            for idx, img in enumerate(captured_images):
                st.image(cv2.cvtColor(img, cv2.COLOR_RGB2BGR), caption=f"Captured Image {idx+1}")
        else:
            st.warning("감지된 이미지가 없습니다.")
    else:
        st.error("비디오 파일을 업로드하세요.")
if st.button("스트림 영상 추출"):
    bell_recorder = BellRecorder()
    bell_recorder.start()
    st.success(f"{bell_recorder.video_filename} 파일이 저장되었습니다.")
    