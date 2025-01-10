import cv2
import mediapipe as mp
import os
import time
from collections import deque
from datetime import datetime
import glob
import pytz

class BellRecorder:
    def __init__(self):
        # 설정 초기화
        self.TARGET_FPS = 20
        self.PRE_RECORD_DURATION = 15
        self.POST_RECORD_DURATION = 15
        self.FRAME_WIDTH = 640
        self.FRAME_HEIGHT = 480
        self.FPS = 20
        self.SAVE_DIR = "recordings"
        os.makedirs(self.SAVE_DIR, exist_ok=True)

        # MediaPipe PoseLandmarker 초기화
        self.pose_landmarker = self.initialize_pose_landmarker()

        # 벨 영역 초기값
        self.BELL_REGION = {"x_min": 0.4, "y_min": 0.4, "x_max": 0.6, "y_max": 0.6}

        # 전역 변수 초기화
        self.recording = False
        self.setting_mode = False
        self.pre_record_buffer = deque(maxlen=self.TARGET_FPS * self.PRE_RECORD_DURATION)
        self.points = []

        # OpenCV 설정
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("카메라를 열 수 없습니다.")

        self.video_writer = None
        self.record_start_time = 0
        self.prev_time = time.time()

        cv2.namedWindow("Video")
        cv2.setMouseCallback("Video", self.on_mouse_click)

    def initialize_pose_landmarker(self):
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions

        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path='pose_landmarker_full.task'),
            running_mode=mp.tasks.vision.RunningMode.VIDEO
        )
        return PoseLandmarker.create_from_options(options)

    def detect_bell_press(self, landmarks):
        """손목 위치가 벨 영역 안에 있는지 확인"""
        left_wrist = landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST]
        for wrist in [left_wrist, right_wrist]:
            if (self.BELL_REGION["x_min"] <= wrist.x <= self.BELL_REGION["x_max"] and
                    self.BELL_REGION["y_min"] <= wrist.y <= self.BELL_REGION["y_max"]):
                return True
        return False

    def on_mouse_click(self, event, x, y, flags, param):
        """마우스 클릭으로 벨 영역 설정"""
        if self.setting_mode and event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))
            if len(self.points) == 2:
                x_min, y_min = self.points[0]
                x_max, y_max = self.points[1]
                self.BELL_REGION = {
                    "x_min": min(x_min, x_max) / self.FRAME_WIDTH,
                    "y_min": min(y_min, y_max) / self.FRAME_HEIGHT,
                    "x_max": max(x_min, x_max) / self.FRAME_WIDTH,
                    "y_max": max(y_min, y_max) / self.FRAME_HEIGHT,
                }
                print(f"벨 영역 설정 완료: {self.BELL_REGION}")
                self.setting_mode = False
                self.points.clear()

    def merge_videos(self):
        """병합된 파일과 다음 파일의 타임스탬프를 비교하여 20초 간격으로 비디오 병합"""
        merge_interval = 20

        video_files = sorted(glob.glob(os.path.join(self.SAVE_DIR, "*.mp4")))
        if not video_files:
            print("병합할 비디오가 없습니다.")
            return

        videos_with_timestamps = [(video, self.parse_timestamp_from_filename(os.path.basename(video)))
                                  for video in video_files]
        videos_with_timestamps = [v for v in videos_with_timestamps if v[1]]
        videos_with_timestamps.sort(key=lambda x: x[1])

        merged_files = []
        current_group = [videos_with_timestamps[0]]

        for i in range(1, len(videos_with_timestamps)):
            prev_video, prev_timestamp = current_group[-1]
            curr_video, curr_timestamp = videos_with_timestamps[i]

            if (curr_timestamp - prev_timestamp).total_seconds() <= merge_interval:
                current_group.append((curr_video, curr_timestamp))
            else:
                merged_file = self.merge_group(current_group)
                merged_files.append((merged_file, self.parse_timestamp_from_filename(os.path.basename(merged_file))))
                current_group = [(curr_video, curr_timestamp)]

        if current_group:
            merged_file = self.merge_group(current_group)
            merged_files.append((merged_file, self.parse_timestamp_from_filename(os.path.basename(merged_file))))

        return merged_files

    def merge_group(self, group):
        """비디오 그룹을 병합하여 하나의 파일로 생성"""
        video_paths = [g[0] for g in group]
        latest_timestamp = max([g[1] for g in group])
        output_filename = latest_timestamp.strftime("%Y%m%d_%H_%M_%S") + ".mp4"
        output_file = os.path.join(self.SAVE_DIR, output_filename)

        cap = cv2.VideoCapture(video_paths[0])
        fps = cap.get(cv2.CAP_PROP_FPS) or self.FPS
        frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or self.FRAME_WIDTH,
                      int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or self.FRAME_HEIGHT)
        cap.release()

        video_writer = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), fps, frame_size)
        for path in video_paths:
            cap = cv2.VideoCapture(path)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                video_writer.write(frame)
            cap.release()

        video_writer.release()
        for path in video_paths:
            if path != output_file:
                self.safe_remove(path)

        return output_file

    def safe_remove(self, file_path):
        try:
            os.remove(file_path)
            print(f"파일 삭제 완료: {file_path}")
        except PermissionError:
            print(f"파일 삭제 실패: {file_path}")

    def parse_timestamp_from_filename(self, filename):
        try:
            return datetime.strptime(os.path.splitext(filename)[0], "%Y%m%d_%H_%M_%S")
        except ValueError:
            return None

    def start(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            current_time = time.time()
            if current_time - self.prev_time < 1 / self.TARGET_FPS:
                continue
            self.prev_time = current_time

            frame = cv2.resize(frame, (self.FRAME_WIDTH, self.FRAME_HEIGHT))
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            timestamp_ms = int(self.cap.get(cv2.CAP_PROP_POS_MSEC))
            results = self.pose_landmarker.detect_for_video(image, timestamp_ms)

            self.pre_record_buffer.append(frame.copy())

            # 벨 영역을 그리기
            x_min, y_min = int(self.BELL_REGION["x_min"] * self.FRAME_WIDTH), int(self.BELL_REGION["y_min"] * self.FRAME_HEIGHT)
            x_max, y_max = int(self.BELL_REGION["x_max"] * self.FRAME_WIDTH), int(self.BELL_REGION["y_max"] * self.FRAME_HEIGHT)
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)

            # pose_landmarks가 유효한 값인지 확인하고, 벨 누름 감지
            if results.pose_landmarks:
                for landmarks in results.pose_landmarks:
                    # landmarks는 list일 수 있으므로 해당 구조에 맞게 접근
                    if self.detect_bell_press(landmarks):  # landmarks는 이미 landmark 리스트일 가능성이 있음
                        if not self.recording:
                            print("벨 누름 감지! 녹화 시작.")
                            self.recording = True
                            self.record_start_time = time.time()

                            kst = pytz.timezone('Asia/Seoul')
                            timestamp = datetime.now(kst).strftime("%Y%m%d_%H_%M_%S")
                            self.video_filename = os.path.join(self.SAVE_DIR, f"{timestamp}.mp4")
                            self.video_writer = cv2.VideoWriter(self.video_filename, cv2.VideoWriter_fourcc(*'mp4v'), self.FPS, (self.FRAME_WIDTH, self.FRAME_HEIGHT))

                            # 녹화 시작 전에 이미지를 버퍼에 저장
                            while self.pre_record_buffer:
                                self.video_writer.write(self.pre_record_buffer.popleft())

            # 녹화 중이라면 비디오 저장
            if self.recording:
                self.video_writer.write(frame)
                if time.time() - self.record_start_time >= self.POST_RECORD_DURATION:
                    print("녹화 완료. 병합 프로세스 시작.")
                    self.recording = False
                    self.merge_videos()
                    self.video_writer.release()

            # 화면에 모드 텍스트 표시
            mode_text = "Click to set bell area" if self.setting_mode else "Press 'S' to set area"
            cv2.putText(frame, mode_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.imshow("Video", frame)

            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.setting_mode = True
                self.points.clear()
                print("설정 모드 활성화: 벨 영역을 클릭하세요")

        self.cap.release()
        cv2.destroyAllWindows()




if __name__ == "__main__":
    bell_recorder = BellRecorder()
    bell_recorder.start()
    bell_recorder.video_filename