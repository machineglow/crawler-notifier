import smtplib

def send_email(message, config):
    server = smtplib.SMTP(config["smtp_server"], config["port"])
    server.starttls()
    server.login(config["sender"], config["password"])
    msg = f"Subject: RFD Keyword Alert\n\n{message}"
    server.sendmail(config["sender"], config["recipient"], msg)
    server.quit()
