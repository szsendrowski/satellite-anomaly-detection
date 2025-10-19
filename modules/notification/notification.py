import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

os.environ["GMAIL_USER"] = "weatheralertspace@gmail.com"
os.environ["GMAIL_APP_PASS"] = "xxxx xxxx xxxx xxxx"
def send_alert_gmail(to_email, subject, html_content):
    gmail_user = os.getenv("GMAIL_USER")
    gmail_pass = os.getenv("GMAIL_APP_PASS")

    if not gmail_user or not gmail_pass:
        raise ValueError("No login data. Set GMAIL_USER and GMAIL_APP_PASS.")

    msg = MIMEMultipart("alternative")
    msg["From"] = gmail_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_pass)
        server.send_message(msg)

    print(f"E-mail sent to {to_email}")

to_email = "recipient's email address"
subject = "🚨 Space Weather Alert – Potential Impact on LEO Operations"
html_content = """
<h2>Space Weather Alert</h2>
<p>The monitoring system has detected increased space weather activity that may affect Low Earth Orbit (LEO) satellite operations.</p>
<p><strong>CME Dynamics Analysis:</strong></p>
<ul>
<li>Velocity: 800 km/s</li>
<li>Estimated mass: 1.60 x 10<sup>8</sup> kg</li>
<li>Kinetic energy: 5.11 × 10<sup>19</sup> J (5.11 × 10<sup>26</sup> erg)</li>
<li>Estimated arrival time: 51.9 h</li>
</ul>
<p><strong>Global risk assessment:</strong></p>
<p><strong>⚠️ MEDIUM risk – CME may partially impact Earth</strong></p>
<p>For more detailed information and updates, please visit our HANS monitoring dashboard:
<a href="https://helioalertnotificationsystem.streamlit.app/CME">Click here</a></p>

"""

send_alert_gmail(to_email, subject, html_content)