pathlib.PosixPath = pathlib.WindowsPath를 통해 posXixPath를 WindowsPath로 대체하는 코드는 포팅이 안되는 코드입니다. 따라서 이 코드는 사용하면 안됩니다. 

대체 코드는 import pathlib와 pathlib.PurePath혹은 pathlib.Path를 사용하는것입니다. 

대체되는 코드는 다음과같습니다.
```python
pathlib.Path
```