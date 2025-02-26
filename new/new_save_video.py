```python
# 경로에서 권한 오류를 피하기 위해 try-except 사용
try:
    os.remove(file_path)
except PermissionError:
    print(f"파일 삭제 실패: {file_path}")

# Thread-safe하게 파일 삭제 करन기 위해 thread-safe 함수 사용
import threading
lock = threading.Lock()

with lock:
    try:
        os.remove(file_path)
    except PermissionError:
        print(f"파일 삭제 실패: {file_path}")

# multiprocessing의 Manager 사용
from multiprocessing import Manager

manager = Manager()
file_path_queue = manager.Queue()

def safe_remove(file_path):
    try:
        os.remove(file_path)
    except PermissionError:
        print(f"파일 삭제 실패: {file_path}")

# multiprocessing 사용
from multiprocessing import Process

def safe_remove_proc(file_path):
    try:
        os.remove(file_path)
    except PermissionError:
        print(f"파일 삭제 실패: {file_path}")

# thread-safe 함수와 Join 사용
import threading

def safe_remove(file_path):
    try:
        os.remove(file_path)
    except PermissionError:
        print(f"파일 삭제 실패: {file_path}")

thread = threading.Thread(target=safe_remove, args=(file_path,))
thread.start()
thread.join()
```