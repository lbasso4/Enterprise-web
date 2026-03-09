from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='engilabstock@gmail.com',
    MAIL_PASSWORD='eyfghkympodiwqwl',
    MAIL_DEFAULT_SENDER='engilabstock@gmail.com')

mail = Mail(app)  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contacte')
def contacte():
    return render_template('contact.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    print("DEBUG request.form:", dict(request.form))
    print("DEBUG content_type:", request.content_type)
    print("DEBUG form dict:", dict(request.form))
    print("DEBUG raw data:", request.get_data(as_text=True))

    nombre = str(request.form.get('name') or request.form.get('nom') or "").strip()
    email = str(request.form.get('email') or "").strip()
    missatge = str(request.form.get('missatge') or "").strip()
    
    body = f"""Nou missatge rebut des del formulari:
        Nom: {nombre or '(sense nom)'}
        Email: {email or '(sense email)'}

        Missatge:
        {missatge or '(sense missatge)'}
        """
    
    recipient = os.environ.get('RECIPIENT_EMAIL', 'engilabstock@gmail.com')
    msg = Message(subject=f'Nou missatge, dubtes de EngiLab: {nombre or '(sense nom)'}', 
    recipients=[recipient],
    body=body)
    
    if email:
            msg.reply_to = email

    #Correu per al client
    if email:
        body_client = f"""Hola {nombre or ''}, 
        
Hem rebut el teu missatge correctament. En breu ens posarem en contacte amb tu.
       
El teu missatge:
{missatge or ''}

Gràcies per contactar amb EngiLab!
"""

    msg_client = Message(
            subject='Hem rebut el teu missatge - EngiLab',
            recipients=[email],
            body=body_client
        )

    try:
        mail.send(msg)
        if email:
            mail.send(msg_client)
        return redirect(url_for('index'))  # Torna a la pàgina principal
    except Exception as e:
        app.logger.exception("Email send failed")
        return "No s'ha pogut enviar el correu ara mateix", 500


if __name__ == '__main__':
    app.run(debug=True)