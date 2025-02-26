```python
    def merge_videos(self):
        merge_interval = 20
        video_files = sorted(glob.glob(os.path.join(self.SAVE_DIR, "*.mp4")))
        if not video_files:
            return

        videos_with_timestamps = []
        for video in video_files:
            timestamp = self.parse_timestamp_from_filename(os.path.basename(video))
            if timestamp:
                videos_with_timestamps.append((video, timestamp))

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
        video_paths = [g[0] for g in group]
        latest_timestamp = max([g[1] for g in group])
        output_filename = latest_timestamp.strftime("%Y%m%d_%H_%M_%S") + ".mp4"
        output_file = os.path.join(self.SAVE_DIR, output_filename)

        try:
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
                    os.remove(path)

            return output_file
        except Exception as e:
            print(f"비디오 병합 중 오류 발생: {e}")
            return None

    def parse_timestamp_from_filename(self, filename):
        try:
            return datetime.strptime(os.path.splitext(filename)[0], "%Y%m%d_%H_%M_%S")
        except ValueError:
            return None

```
