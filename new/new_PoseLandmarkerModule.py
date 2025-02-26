send_email 함수의 smtp 서버 연결 부분의 보안 취약점

`server.starttls()` 대신 `server.startssl()`을 사용합니다.

 However, since you're using Gmail's SMTP server, you should use `server.starttls()` instead of `server.startssl()`. But to make it more secure, you can use the following code:

```python
server = smtplib.SMTP_SSL(smtp_server, smtp_port)
```

또한, `server.login(username, password)`에서 비밀번호를 평문으로 전달하는 것은 보안 취약점입니다. 이를 대신하여 OAuth 2.0을 사용하여 인증할 수 있습니다.

```python
import base64
auth_string = f'{username}:{password}'
auth_string = base64.b64encode(auth_string.encode()).decode()
server.docmd('AUTH', 'XOAUTH2 ' + auth_string)
```