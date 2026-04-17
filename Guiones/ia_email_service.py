import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"D:\AGENTE_IA\.env")

def send_ia_email(to_email, subject, body):
    """Envía un email usando SMTP y cierra la conexión inmediatamente."""
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_user or "tu-email" in smtp_user:
        print("Aviso: Credenciales SMTP no configuradas. Simulando envío...")
        print(f"A: {to_email} | Asunto: {subject} | Cuerpo: {body[:50]}...")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"Email enviado exitosamente a {to_email}")
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False

if __name__ == "__main__":
    # Prueba rápida
    send_ia_email("test@ejemplo.com", "Prueba AGENTE IA", "Este es un mensaje de prueba del sistema de feedback.")
