비밀번호를 안전하게 저장할 수 있도록 `st.sidebar.text_input` 함수의 `type` 매개변수를 `"password"` 대신 `st.sidebar`의 `text_input` 함수와 함께 `forms`를 사용하여 안전하게 비밀번호를 입력 받을 수 있습니다. 

예를 들어, 아래와 같이 비밀번호를 안전하게 입력 받을 수 있습니다.
```python
import streamlit as st

with st.form("email_info"):
    smtp_server = st.text_input("SMTP 서버", "smtp.gmail.com")
    smtp_port = st.number_input("SMTP 포트", value=587)
    username = st.text_input("이메일 주소", "gnfmcm333@gmail.com")
    password = st.text_input("비밀번호", type="password")
    to_email = st.text_input("받는 이메일 주소", "gnfmcm333@gmail.com")
    email_info = {
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "username": username,
        "password": password,
        "to_email": to_email
    }
    submitted = st.form_submit_button("제출")
    if submitted:
        # 비밀번호를 안전하게 저장
        # ...
```