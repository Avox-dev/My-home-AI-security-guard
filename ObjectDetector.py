import cv2
import torch
import pathlib
import sys
# pathlib의 경로 설정 수정
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

class ObjectDetector:
    def __init__(self, model_path: str, weights_path: str):
        """
        모델을 초기화하고 객체 감지를 위한 준비를 합니다.
        """
        #sys.path.insert(0, r'C:/Users/user/Desktop/SK_Shieldus/python_project')#yolov5 폴더가 있는 경로로
        
        # 모델 로드
        self.model = torch.hub.load(model_path, 'custom', path=weights_path, source='local', force_reload=True)
        self.model.eval()

    def detect_objects(self, image_path: str):
        """
        주어진 이미지에서 객체를 감지하고, 감지된 객체의 수와 수정된 이미지를 반환합니다.
        """
        # 이미지 읽기
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"이미지를 읽을 수 없습니다: {image_path}")
            return 0, None

        # 모델 입력 크기 640x640으로 크기 조정
        resized_frame = cv2.resize(frame, (640, 640))

        # 모델 예측
        results = self.model(resized_frame)

        # 예측 결과
        prediction = results.xyxy[0].cpu().numpy()  # 예측된 좌표와 정보 추출

        object_count = 0  # 감지된 객체 수 초기화

        # 객체 감지된 정보 그리기
        for pred in prediction:
            x_min, y_min, x_max, y_max, conf, cls = pred
            if conf > 0.9:  # 신뢰도 90% 이상만 처리
                object_count += 1  # 객체 카운트 증가

                # 객체의 좌표로 사각형 그리기 (이미지 크기 비율에 맞게 되돌리기)
                x_min = int(x_min * frame.shape[1] / 640)
                y_min = int(y_min * frame.shape[0] / 640)
                x_max = int(x_max * frame.shape[1] / 640)
                y_max = int(y_max * frame.shape[0] / 640)

                # 사각형 그리기
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)  # 초록색 사각형

                # 라벨 및 신뢰도 표시
                label = f'{self.model.names[int(cls)]} {conf:.2f}'  # 클래스 이름과 신뢰도
                cv2.putText(frame, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # 감지된 객체 수 리턴
        return object_count, frame

    def show_detected_image(self, image_path: str):
        """
        객체를 감지한 이미지를 표시하고 객체의 수를 출력하는 함수.
        """
        object_count, annotated_image = self.detect_objects(image_path)

        if annotated_image is not None:
            # 감지된 객체 수 출력
            return object_count
            # 객체가 감지된 이미지를 표시
            #cv2.imshow('Detected Image', annotated_image)

            # 'ESC' 키를 누르면 종료
            #cv2.waitKey(0)

            # 자원 해제
            #cv2.destroyAllWindows()

if __name__ == "__main__":
    # 모델 경로 및 가중치 경로
    model_path = "yolov5"
    weights_path = 'best.pt'

    # 이미지 경로
    image_path = 'box.jpg'

    # 객체 탐지기 객체 생성
    detector = ObjectDetector(model_path, weights_path)

    # 이미지에서 객체를 감지하고 결과를 표시
    detector.show_detected_image(image_path)
