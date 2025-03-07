def test_email():
    try:
        server = smtplib.SMTP(mail.settings.server)
        server.set_debuglevel(1)  # Isso vai mostrar todo o diálogo SMTP
        server.ehlo()
        if mail.settings.tls:
            server.starttls()
        server.login(configuration.get('smtp.username'), configuration.get('smtp.password'))
        server.quit()
        return "Conexão bem sucedida!"
    except Exception as e:
        return f"Erro na conexão: {str(e)}"