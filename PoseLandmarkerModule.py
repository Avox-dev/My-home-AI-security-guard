import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
from mediapipe.python.solutions import drawing_utils, drawing_styles, pose
import numpy as np
import cv2
import time
import os
from ObjectDetector import ObjectDetector

class PoseLandmarkerModule:
    def __init__(self, model_path, video_path, region, email_info):
        self.model_path = model_path
        self.video_path = video_path
        self.region = region
        self.timer = {}
        self.landmarker = self.initialize_pose_landmarker()
        model_path = "yolov5"
        weights_path = 'best.pt'
        self.object_detector = ObjectDetector(model_path, weights_path)
        self.parcel_count = 0
        self.last_detected_time = 0  # 택배기사 감지 시간을 기록할 변수 추가
        self.detect_cooldown = 10  # 감지 후 10초 동안 비활성화
        self.email_info = email_info  # 이메일 정보 추가
        self.drawing_region = False  # 영역 드래그 중인지 확인하는 플래그
        self.start_point = None      # 드래그 시작점
        self.region = region

    def initialize_pose_landmarker(self):
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions

        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self.model_path),
            running_mode=mp.tasks.vision.RunningMode.VIDEO
        )
        return PoseLandmarker.create_from_options(options)

    def draw_landmarks_on_image(self, rgb_image, detection_result):
        pose_landmarks_list = detection_result.pose_landmarks
        annotated_image = np.copy(rgb_image)

        # 모든 포즈 랜드마크를 이미지에 그리기
        for idx in range(len(pose_landmarks_list)):
            pose_landmarks = pose_landmarks_list[idx]
            pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            pose_landmarks_proto.landmark.extend(
                [landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks]
            )
            drawing_utils.draw_landmarks(
                annotated_image,
                pose_landmarks_proto,
                pose.POSE_CONNECTIONS,
                drawing_styles.get_default_pose_landmarks_style()
            )
        return annotated_image
    def on_mouse_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # 마우스 왼쪽 버튼 누름
            self.drawing_region = True
            self.start_point = (x, y)
        
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing_region:  # 마우스 이동
            # 드래그 중에 영역 실시간으로 업데이트
            self.region['x_min'] = min(self.start_point[0], x)
            self.region['x_max'] = max(self.start_point[0], x)
            self.region['y_min'] = min(self.start_point[1], y)
            self.region['y_max'] = max(self.start_point[1], y)

        elif event == cv2.EVENT_LBUTTONUP:  # 마우스 왼쪽 버튼 떼기
            self.drawing_region = False

    def check_doorbell_press(self, pose_landmarks, frame, min_duration=0.1):
        current_time = time.time()
        if current_time - self.last_detected_time < self.detect_cooldown:
            remaining_time = self.detect_cooldown - (current_time - self.last_detected_time)
            print(f"\r택배기사 감지 후 {int(remaining_time)}초 남았습니다...", end='', flush=True)
            return None

        LEFT_WRIST = 15
        RIGHT_WRIST = 16

        left_wrist = pose_landmarks[LEFT_WRIST]
        right_wrist = pose_landmarks[RIGHT_WRIST]

        frame_width, frame_height = frame.shape[1], frame.shape[0]

        def is_in_region(wrist):
            x, y = int(wrist.x * frame_width), int(wrist.y * frame_height)
            return (
                self.region["x_min"] <= x <= self.region["x_max"]
                and self.region["y_min"] <= y <= self.region["y_max"]
            )

        left_in_region = is_in_region(left_wrist)
        right_in_region = is_in_region(right_wrist)

        if left_in_region or right_in_region:
            if "press" not in self.timer:
                self.timer["press"] = current_time
            elif current_time - self.timer["press"] >= min_duration:
                print("\n초인종 누르기 동작이 감지되었습니다!")
                self.timer.clear()
                captured_image = self.capture_frame(frame)
                cv2.imwrite('output_image.jpg', captured_image)
                doorbell_parcel_count = self.object_detector.show_detected_image('output_image.jpg')
                if self.parcel_count != doorbell_parcel_count:
                    print('택배기사입니다.')
                    self.parcel_count = doorbell_parcel_count
                    
                    # 택배기사를 감지하면 이메일 전송
                    self.send_email(captured_image,'택배기사 감지 알림', '택배기사가 감지되었습니다. 아래 사진을 확인하세요.')
                elif self.parcel_count == doorbell_parcel_count:
                    print('택배기사가 아닙니다.')
                    # 이상자를 감지하면 이메일 전송
                    self.send_email(captured_image,'이상자 감지 알림', '이상자가 감지되었습니다. 아래 사진을 확인하세요.')
                self.last_detected_time = current_time
                return captured_image
        else:
            self.timer.pop("press", None)
        
        return None

    def capture_frame(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def process_video(self):
        video_capture = cv2.VideoCapture(self.video_path)
        if not video_capture.isOpened():
            print("비디오를 열 수 없습니다. 경로를 확인하세요.")
            return None

        captured_images = []  # 캡처된 이미지들을 저장할 리스트

        # OpenCV 윈도우에 마우스 콜백 연결
        cv2.namedWindow('Pose Detection')
        cv2.setMouseCallback('Pose Detection', self.on_mouse_event)

        with self.landmarker:
            while video_capture.isOpened():
                success, frame = video_capture.read()
                if not success:
                    print("프레임 읽기 실패.")
                    break

                aspect_ratio = frame.shape[1] / frame.shape[0]
                resize_width = 640
                resize_height = int(resize_width / aspect_ratio)
                frame = cv2.resize(frame, (resize_width, resize_height))

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

                timestamp_ms = int(video_capture.get(cv2.CAP_PROP_POS_MSEC))
                pose_landmarker_result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

                if pose_landmarker_result.pose_landmarks:
                    landmarks = pose_landmarker_result.pose_landmarks[0]
                    captured_image = self.check_doorbell_press(landmarks, frame, min_duration=1.0)
                    if captured_image is not None:
                        captured_images.append(captured_image)

                annotated_frame = self.draw_landmarks_on_image(frame_rgb, pose_landmarker_result)

                # 드래그로 업데이트된 영역 그리기
                cv2.rectangle(annotated_frame,
                              (self.region['x_min'], self.region['y_min']),
                              (self.region['x_max'], self.region['y_max']),
                              (0, 255, 0), 2)
                cv2.imshow('Pose Detection', cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR))

                if cv2.waitKey(5) & 0xFF == 27:  # ESC 키로 종료
                    break

        video_capture.release()
        cv2.destroyAllWindows()

        return captured_images

    def send_email(self, image_array, subject, body):
        # 이미지 데이터를 임시 파일로 저장
        image_path = 'temp_image.jpg'
        cv2.imwrite(image_path, cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR))  # 임시 파일로 저장

        # 이메일 서버 설정
        smtp_server = self.email_info['smtp_server']
        smtp_port = self.email_info['smtp_port']
        username = self.email_info['username']
        password = self.email_info['password']
        to_email = self.email_info['to_email']

        # 이메일 메시지 작성
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to_email
        msg['Subject'] = subject

        # 본문 추가
        msg.attach(MIMEText(body, 'plain'))

        # 이미지 첨부
        with open(image_path, 'rb') as img:
            image = MIMEImage(img.read())
            image.add_header('Content-Disposition', 'attachment', filename='detected_image.jpg')
            msg.attach(image)

        # 이메일 보내기
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # 보안 연결
                server.login(username, password)
                server.sendmail(username, to_email, msg.as_string())
                print("이메일이 성공적으로 전송되었습니다.")
        except Exception as e:
            print(f"이메일 전송 오류: {e}")

        # 임시 파일 삭제
        if os.path.exists(image_path):
            os.remove(image_path)

# 실행
if __name__ == "__main__":
    model_path = 'pose_landmarker_full.task'
    video_path = 'C021_A17_SY16_P07_S12_02NBS.mp4'

    region = {
        'x_min': 350,
        'x_max': 400,
        'y_min': 75,
        'y_max': 125
    }

    email_info = {  # 이메일 정보 예시
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'gnfmcm333@gmail.com',
        'password': 'bhef qdax umfu bnbi',
        'to_email': 'gnfmcm333@gmail.com'
    }

    pose_landmarker = PoseLandmarkerModule(model_path, video_path, region, email_info)
    captured_images = pose_landmarker.process_video()

    if captured_images:
        print(f"총 {len(captured_images)}개의 캡처된 이미지가 있습니다.")
        for idx, img in enumerate(captured_images):
            cv2.imshow(f'Captured Image {idx+1}', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            cv2.waitKey(0)
        cv2.destroyAllWindows()