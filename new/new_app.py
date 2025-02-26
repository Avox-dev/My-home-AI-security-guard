비밀번호를 직접 코드에 하드코딩하는 것은 매우 위험합니다.  이메일 정보는 환경 변수 또는 암호화된 설정 파일을 사용하여 관리해야 합니다.  Streamlit Secrets 또는 다른 비밀 관리 솔루션을 활용하는 것을 강력히 권장합니다.


아래는  `email_info`  딕셔너리를  환경변수에서 읽어오는 방식으로 수정한 코드의 핵심 부분입니다.  전체 코드를 수정하려면  `email_info`  딕셔너리 생성 부분을 이 코드로 대체하고,  `PoseLandmarkerModule`  클래스가 환경변수를 사용할 수 있도록 수정해야 합니다.

```python
import os

email_info = {
    "smtp_server": os.environ.get("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.environ.get("SMTP_PORT", 587)),
    "username": os.environ.get("EMAIL_USERNAME"),
    "password": os.environ.get("EMAIL_PASSWORD"),
    "to_email": os.environ.get("EMAIL_TO")
}

# ... (나머지 코드) ...
```

이 코드는 환경 변수에서 이메일 정보를 읽어옵니다.  환경 변수가 설정되지 않으면 기본값을 사용합니다.  실행 전에  `SMTP_SERVER`, `SMTP_PORT`, `EMAIL_USERNAME`, `EMAIL_PASSWORD`, `EMAIL_TO`  환경 변수를 시스템 환경 변수 또는 Streamlit Secrets를 통해 설정해야 합니다.  예를 들어,  Linux/macOS  에서는 다음과 같이 설정할 수 있습니다.

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export EMAIL_USERNAME="your_email@gmail.com"
export EMAIL_PASSWORD="your_password"
export EMAIL_TO="recipient_email@example.com"
```

**중요:**  암호를 직접 명령어에 넣는 것은 매우 위험합니다.  다른 안전한 방법 (예:  secrets management tool)을 사용하십시오.  이 예시는 이해를 돕기 위한 목적으로만 제공됩니다.
