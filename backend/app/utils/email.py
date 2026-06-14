import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_credentials_email(
    smtp_host, smtp_port, smtp_user, smtp_password,
    smtp_from, smtp_from_name, app_url, to_email, name, password
):
    if not smtp_host or not smtp_user:
        print(f"[EMAIL] SMTP nao configurado. Credenciais para {to_email}: {password}")
        return False
    display_name = name or "advogado(a)"
    subject = "Suas credenciais de acesso - Honorarios PRO"
    from_addr = smtp_from or smtp_user
    html_body = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;"><div style="max-width:560px;margin:40px auto;background:#fff;border-radius:10px;overflow:hidden;"><div style="background:#1B2A4A;padding:32px 40px;"><h1 style="color:#C9A84C;margin:0;font-size:22px;">Honorarios PRO</h1></div><div style="padding:32px 40px;"><h2 style="color:#1B2A4A;margin-top:0;">Bem-vindo(a), {display_name}!</h2><p style="color:#444;">Seu acesso foi ativado. Use as credenciais abaixo:</p><div style="background:#f8f8f8;border-left:4px solid #C9A84C;padding:20px 24px;border-radius:4px;margin:24px 0;"><p style="margin:0 0 8px;color:#666;font-size:13px;">EMAIL</p><p style="margin:0 0 16px;color:#1B2A4A;font-weight:bold;">{to_email}</p><p style="margin:0 0 8px;color:#666;font-size:13px;">SENHA</p><p style="margin:0;color:#1B2A4A;font-size:22px;font-weight:bold;letter-spacing:2px;">{password}</p></div><a href="{app_url}" style="display:inline-block;background:#1B2A4A;color:#fff;padding:14px 32px;text-decoration:none;border-radius:6px;font-weight:bold;">Acessar agora</a><p style="color:#888;font-size:12px;border-top:1px solid #eee;padding-top:16px;margin-top:24px;">Recomendamos alterar sua senha apos o primeiro acesso.</p></div></div></body></html>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{smtp_from_name} <{from_addr}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_addr, to_email, msg.as_string())
        print(f"[EMAIL] Credenciais enviadas para {to_email}")
        return True
    except Exception as e:
        print(f"[EMAIL] Erro ao enviar para {to_email}: {e}")
        return False
