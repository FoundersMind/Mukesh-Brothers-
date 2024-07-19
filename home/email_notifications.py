import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_inventory_alert_email(request, alert_message):
    seller = request.user  # Assuming the user is a seller
    subject = 'Low Inventory Alert'
    message = alert_message
    from_email = '2105470@kiit.ac.in'  
    recipient_email = 'njbhandari4@gmail.com'

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    body = f"Dear {seller.username},\n\n{message}\n\nSincerely,\nThe Inventory System"
    msg.attach(MIMEText(body, 'plain'))

    # Replace these with your actual SMTP server and authentication details
    SMTP_SERVER = 'your-smtp-server.com'
    SMTP_PORT = 587
    SMTP_USERNAME = 'your-email@example.com'
    SMTP_PASSWORD = 'your-email-password'

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(from_email, recipient_email, msg.as_string())

# Example usage:
# send_inventory_alert_email(request, "Your inventory is running low.")
