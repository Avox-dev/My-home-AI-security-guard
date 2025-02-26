```python
    def send_email(self, image_array, subject, body):
        # 이미지 데이터를 base64로 인코딩
        _, buffer = cv2.imencode(".jpg", cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR))
        encoded_image = base64.b64encode(buffer).decode("utf-8")

        # 이메일 메시지 작성 (base64 인코딩된 이미지 포함)
        msg = MIMEMultipart()
        msg['From'] = self.email_info['username']
        msg['To'] = self.email_info['to_email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # 이미지를 base64로 인코딩된 문자열로 첨부
        img_attachment = MIMEText(encoded_image, 'base64')
        img_attachment.add_header('Content-Disposition', 'attachment; filename="detected_image.jpg"')
        msg.attach(img_attachment)

        # 이메일 보내기 (임시 파일 생성 없이 직접 전송)
        try:
            with smtplib.SMTP(self.email_info['smtp_server'], self.email_info['smtp_port']) as server:
                server.starttls()
                server.login(self.email_info['username'], self.email_info['password'])
                server.sendmail(self.email_info['username'], self.email_info['to_email'], msg.as_string())
                print("이메일이 성공적으로 전송되었습니다.")
        except Exception as e:
            print(f"이메일 전송 오류: {e}")

```
