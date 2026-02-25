from flask import Flask, render_template, request
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='blanca.navas.cerezuela@estudiantat.upc.edu',
    MAIL_PASSWORD='qwdffpnqxcaffsyi',
    MAIL_DEFAULT_SENDER='blanca.navas.cerezuela@estudiantat.upc.edu')

mail = Mail(app)  
@app.route('/prova')
def prova():
    return render_template('prova.html') 

@app.route('/')
def index():
    return render_template('contact.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    print("DEBUG request.form:", dict(request.form))
    print("DEBUG content_type:", request.content_type)
    print("DEBUG form dict:", dict(request.form))
    print("DEBUG raw data:", request.get_data(as_text=True))

    nombre = str(request.form.get('name') or request.form.get('nom') or "").strip()
    email = str(request.form.get('email') or "").strip()
    
    body = f"""Nou missatge rebut des del formulari:
        Nom: {nombre or '(sense nom)'}
        Email: {email or '(sense email)'}

        Missatge:
        {missatge or '(sense missatge)'}
        """
    
    recipient = os.environ.get('RECIPIENT_EMAIL', 'blanca.navas.cerezuela@estudiantat.upc.edu')
    msg = Message(subject=f'Nou missatge, dubtes de EngiLab: {nombre or '(sense nom)'}', 
    recipients=[recipient],
    body=body)
    
    if email:
            msg.reply_to = email
    try:
        mail.send(msg)
        return 'Formulari enviat correctament'
    except Exception as e:
        app.logger.exception("Email send failed")
        return "No s'ha pogut enviar el correu ara mateix", 500


if __name__ == '__main__':
    app.run(debug=True)
