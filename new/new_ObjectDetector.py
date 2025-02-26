`temp = pathlib.PosixPath; pathlib.PosixPath = pathlib.WindowsPath` 는 안정적이지 않은 코드로, 경로를 설정하는 방법으로 아래의 방법 대신합니다.

```python
import os
os.chdir('C:/Users/user/Desktop/SK_Shieldus/python_project')
```