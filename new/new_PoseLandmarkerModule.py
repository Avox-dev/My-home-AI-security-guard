리눅스에서 사용될 경우 가장 위험한 취약점은 패스워드가明文으로 노출되어 있다는 것이다. 이를 해결하기 위해 비밀번호를 환경 변수나 güvenli한 저장소에 넣는 방법이 있다. 

다음과 같이 `email_info`에 비밀번호를 넣는代わりに 환경 변수를 사용할 수 있다.

```python
import os

email_info = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'gnfmcm333@gmail.com',
    'password': os.environ.get('EMAIL_PASSWORD'),  # 환경 변수에서 비밀번호 얻기
    'to_email': 'gnfmcm333@gmail.com'
}
```

그뒤에, 환경 변수를 설정해야 한다. 

리눅스 또는 맥에서 다음과 같이 실행하여 환경 변수를 설정할 수 있다.

```bash
export EMAIL_PASSWORD='your_password'
```

윈도우의 경우 다음과 같이 환경 변수를 설정할 수 있다.

```bash
set EMAIL_PASSWORD='your_password'
```