import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

def test_smtp_connection():
    load_dotenv()
    
    server_host = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    try:
        server_port = int(os.getenv('MAIL_PORT', 587))
    except:
        server_port = 587
        
    username = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    sender = os.getenv('MAIL_DEFAULT_SENDER')

    print("--- DIAGNÓSTICO DE CORREO ---")
    print(f"Servidor: {server_host}")
    print(f"Puerto: {server_port}")
    print(f"Usuario: {username}")
    print(f"Remitente: {sender}")
    print(f"¿Password configurada?: {'SÍ' if password else 'NO'}")
    
    if not username or not password:
        print("\nERROR: Faltan credenciales en el archivo .env")
        return

    msg = EmailMessage()
    msg.set_content("Esta es una prueba de conexión SMTP desde tu app Mercado.")
    msg['Subject'] = "Prueba de Diagnóstico Mercado"
    msg['From'] = sender
    msg['To'] = username # Te lo envías a ti mismo

    try:
        print("\nConectando al servidor...")
        # Cambiar a SMTP_SSL si el puerto es 465, si no usar starttls en 587
        if server_port == 465:
            server = smtplib.SMTP_SSL(server_host, server_port)
        else:
            server = smtplib.SMTP(server_host, server_port)
            server.starttls()
            
        print("Intentando iniciar sesión...")
        server.login(username, password)
        
        print("Enviando mensaje de prueba...")
        server.send_message(msg)
        server.quit()
        print("\n¡ÉXITO! El correo se envió correctamente.")
        print("Si no lo ves en tu bandeja de entrada, revisa la carpeta de SPAM.")
        
    except smtplib.SMTPAuthenticationError:
        print("\nERROR DE AUTENTICACIÓN: El usuario o la contraseña son incorrectos.")
        if "gmail" in server_host.lower():
            print("NOTA: Para Gmail debes usar una 'Contraseña de Aplicación', no tu clave normal.")
    except Exception as e:
        print(f"\nERROR INESPERADO: {e}")

if __name__ == "__main__":
    test_smtp_connection()
