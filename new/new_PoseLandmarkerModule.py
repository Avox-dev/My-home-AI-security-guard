```python
    def send_email(self, image_array, subject, body):
        # 이미지 데이터를 base64로 인코딩
        _, encoded_image = cv2.imencode('.jpg', cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR))
        encoded_string = base64.b64encode(encoded_image).decode('utf-8')

        # 이메일 메시지 작성 (HTML 형식 사용)
        msg = MIMEMultipart('alternative')
        msg['From'] = self.email_info['username']
        msg['To'] = self.email_info['to_email']
        msg['Subject'] = subject

        text_part = MIMEText(body, 'plain')
        html_part = MIMEText(f'<html><body><p>{body}</p><img src="data:image/jpeg;base64,{encoded_string}"></body></html>', 'html')
        msg.attach(text_part)
        msg.attach(html_part)

        # 이메일 보내기 (smtplib 부분은 변경하지 않음)
        try:
            with smtplib.SMTP(self.email_info['smtp_server'], self.email_info['smtp_port']) as server:
                server.starttls()
                server.login(self.email_info['username'], self.email_info['password'])
                server.sendmail(self.email_info['username'], self.email_info['to_email'], msg.as_string())
                print("이메일이 성공적으로 전송되었습니다.")
        except Exception as e:
            print(f"이메일 전송 오류: {e}")

```
