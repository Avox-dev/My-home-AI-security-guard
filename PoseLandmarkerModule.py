import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
from mediapipe.python.solutions import drawing_utils, drawing_styles, pose
import numpy as np
import cv2
import time
from ObjectDetector import ObjectDetector

class PoseLandmarkerModule:
    def __init__(self, model_path, video_path, region):
        self.model_path = model_path
        self.video_path = video_path
        self.region = region
        self.timer = {}
        self.landmarker = self.initialize_pose_landmarker()
        model_path = "yolov5"
        weights_path = 'best.pt'
        self.object_detector = ObjectDetector(model_path, weights_path)
        self.parcel_count = 0
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

    def check_doorbell_press(self, pose_landmarks, frame, min_duration=1.0):
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
        current_time = time.time()

        # 타이머 갱신
        if left_in_region or right_in_region:
            if "press" not in self.timer:
                self.timer["press"] = current_time
            elif current_time - self.timer["press"] >= min_duration:
                print("초인종 누르기 동작이 감지되었습니다!")
                self.timer.clear()
                # 캡처된 프레임을 변수로 리턴
                captured_image = self.capture_frame(frame)
                cv2.imwrite('output_image.jpg', captured_image)
                # ObjectDetector에서 캡처된 이미지로 객체 탐지
                doorbell_parcel_count=self.object_detector.show_detected_image('output_image.jpg')  # 객체 탐지 수행
                if self.parcel_count != doorbell_parcel_count:
                    print('택배기사입니다.')
                    self.parcel_count=doorbell_parcel_count
                elif self.parcel_count == doorbell_parcel_count:
                    print('택배기사가 아닙니다.')
                return captured_image
        else:
            self.timer.pop("press", None)
        
        return None

    def capture_frame(self, frame):
        """
        초인종을 누를 때 현재 프레임을 캡처하고 변수로 반환하는 메소드
        """
        # 프레임을 RGB로 변환하여 반환
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def process_video(self):
        video_capture = cv2.VideoCapture(self.video_path)
        if not video_capture.isOpened():
            print("비디오를 열 수 없습니다. 경로를 확인하세요.")
            return None  # 비디오를 열 수 없으면 None 반환

        captured_images = []  # 캡처된 이미지들을 저장할 리스트

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
                    captured_image = self.check_doorbell_press(
                        landmarks, frame, min_duration=1.0
                    )
                    if captured_image is not None:
                        # 초인종 감지 후 캡처된 이미지를 저장
                        captured_images.append(captured_image)
                
                annotated_frame = self.draw_landmarks_on_image(frame_rgb, pose_landmarker_result)
                # 지정된 영역을 사각형으로 그리기
                cv2.rectangle(annotated_frame,
                              (self.region['x_min'], self.region['y_min']),
                              (self.region['x_max'], self.region['y_max']),
                              (0, 255, 0), 2)
                cv2.imshow('Pose Detection', cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR))

                if cv2.waitKey(5) & 0xFF == 27:
                    break

        video_capture.release()
        cv2.destroyAllWindows()

        # 캡처된 이미지를 반환
        return captured_images

# 실행
if __name__ == "__main__":
    model_path = 'pose_landmarker_full.task'
    video_path = 'testVideo.mp4'#r'C:\Users\user\Downloads\116.주거 및 공용 공간 내 이상행동 영상 데이터\01.데이터\1.Training\원천데이터\TS15\주거침입-문\초인종을 계속 누름\테스트C021_A17_SY16_P07_S14_01DAS.mp4'

    region = {
        'x_min': 350,
        'x_max': 400,
        'y_min': 75,
        'y_max': 125
    }

    pose_landmarker = PoseLandmarkerModule(model_path, video_path, region)
    captured_images = pose_landmarker.process_video()

    if captured_images:
        print(f"총 {len(captured_images)}개의 캡처된 이미지가 있습니다.")
        for idx, img in enumerate(captured_images):
            cv2.imshow(f'Captured Image {idx+1}', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            cv2.waitKey(0)
        cv2.destroyAllWindows()
