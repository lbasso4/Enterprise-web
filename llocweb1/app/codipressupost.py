from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_mail import Mail, Message
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
import io
from datetime import datetime
from app import app

CORS(app)

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='engilabstock@gmail.com',
    MAIL_PASSWORD='eyfghkympodiwqwl',
    MAIL_DEFAULT_SENDER='engilabstock@gmail.com'
)
mail = Mail(app)

@app.route('/pressupost')
def pressupost():
    return render_template('pressupost.html')
# ── Dades EngiLab ──
NOM_EMPRESA  = 'EngiLab ETSEIB'
EMAIL_ENG    = 'engilabstock@gmail.com'

# ── Preus ──
preus_materials_g = {
    'Fil PLA':     0.075,
    'Fusta':       0.030,
    'Metacrilat':  0.050,
    'Vinil':       0.020,
}

preus_serveis = {
    'Impresió 3D':           0.10,
    'Gravat i tall làser':   0.15,
    'Escanejat 3D':          0.08,
    'Estampació':            0.12,
    'Impressió 3D resina':   0.20,
    'Plaques electròniques': 0.18,
}


# ── Generació del PDF ──
def generar_pdf(client, materials):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    contingut = []
    estils = getSampleStyleSheet()

    estil_titol = ParagraphStyle(
        'titol', parent=estils['Title'],
        fontSize=20, textColor=colors.HexColor('#007bc1'), spaceAfter=6
    )
    estil_subtitol = ParagraphStyle(
        'subtitol', parent=estils['Normal'],
        fontSize=10, textColor=colors.HexColor('#6b7280'), spaceAfter=16
    )
    estil_seccio = ParagraphStyle(
        'seccio', parent=estils['Normal'],
        fontSize=11, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a1a2e'), spaceBefore=14, spaceAfter=6
    )
    estil_normal = ParagraphStyle(
        'normal_custom', parent=estils['Normal'],
        fontSize=10, textColor=colors.HexColor('#374151')
    )

    # ── Capçalera ──
    contingut.append(Paragraph('PRESSUPOST AL CLIENT', estil_titol))
    contingut.append(Spacer(1, 0.8*cm))
    contingut.append(Paragraph(f'{NOM_EMPRESA}  ·  {EMAIL_ENG}', estil_subtitol))
    contingut.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#007bc1')))
    contingut.append(Spacer(1, 0.4*cm))

    # ── Dades del client ──
    contingut.append(Paragraph('Dades del client', estil_seccio))
    dades_taula = [
        ['Nom i cognoms',       client.get('nom', '')],
        ['Adreça electrònica',  client.get('email', '')],
        ['Relació amb el centre', client.get('relacio', '')],
        ['Data de sol·licitud', datetime.now().strftime('%d/%m/%Y')],
    ]
    taula_client = Table(dades_taula, colWidths=[5*cm, 12*cm])
    taula_client.setStyle(TableStyle([
        ('FONTNAME',   (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, -1), 10),
        ('TEXTCOLOR',  (0, 0), (0, -1), colors.HexColor('#007bc1')),
        ('TEXTCOLOR',  (1, 0), (1, -1), colors.HexColor('#1a1a2e')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f2f4f7')]),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.HexColor('#e8eaed')),
        ('PADDING',    (0, 0), (-1, -1), 8),
    ]))
    contingut.append(taula_client)
    contingut.append(Spacer(1, 0.4*cm))

    # ── Descripció del projecte ──
    contingut.append(Paragraph('Descripció del projecte', estil_seccio))
    contingut.append(Paragraph(client.get('descripcio', '(sense descripció)'), estil_normal))
    contingut.append(Spacer(1, 0.4*cm))

    # ── Taula de materials i serveis ──
    contingut.append(Paragraph('Materials i serveis', estil_seccio))

    cap = [['Servei', 'Material', 'Gast', 'Preu unitari', 'Subtotal']]
    total_general = 0.0

    for m in materials:
        servei   = m.get('servei', '')
        material = m.get('material', '')
        try:
            gast = float(m.get('gast', 0) or 0)
        except ValueError:
            gast = 0.0

        preu_mat = preus_materials_g.get(material, 0)
        preu_ser = preus_serveis.get(servei, 0)
        preu_u   = preu_mat + preu_ser
        subtotal = round(preu_u * gast, 2)
        total_general += subtotal

        cap.append([
            servei,
            material,
            f'{gast} g',
            f'{preu_u:.3f} €/g',
            f'{subtotal:.2f} €'
        ])

    # Fila total
    cap.append(['', '', '', 'TOTAL', f'{total_general:.2f} €'])

    taula_mat = Table(cap, colWidths=[4.5*cm, 3.5*cm, 2*cm, 3*cm, 2.5*cm])
    taula_mat.setStyle(TableStyle([
        # Capçalera
        ('BACKGROUND',  (0, 0), (-1, 0),  colors.HexColor('#007bc1')),
        ('TEXTCOLOR',   (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',    (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, 0),  10),
        # Files de dades
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
        ('FONTSIZE',    (0, 1), (-1, -1), 9),
        # Fila total
        ('BACKGROUND',  (0, -1), (-1, -1), colors.HexColor('#f2f4f7')),
        ('FONTNAME',    (3, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR',   (3, -1), (-1, -1), colors.HexColor('#007bc1')),
        # General
        ('ALIGN',       (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID',        (0, 0), (-1, -1), 0.5, colors.HexColor('#e8eaed')),
        ('PADDING',     (0, 0), (-1, -1), 7),
    ]))
    contingut.append(taula_mat)
    contingut.append(Spacer(1, 0.6*cm))

    # ── Peu de pàgina ──
    contingut.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e8eaed')))
    contingut.append(Spacer(1, 0.2*cm))
    contingut.append(Paragraph(
        f'Document generat automàticament per {NOM_EMPRESA} · {datetime.now().strftime("%d/%m/%Y %H:%M")}',
        ParagraphStyle('peu', parent=estils['Normal'], fontSize=8, textColor=colors.HexColor('#9ca3af'), alignment=1)
    ))

    doc.build(contingut)
    buffer.seek(0)
    return buffer.read()

@app.route('/generar', methods=['POST'])
def generar():
    # Llegir camps del formulari
    client = {
        'nom':       request.form.get('nom', ''),
        'email':     request.form.get('email', ''),
        'relacio':   request.form.get('relacio', ''),
        'descripcio': request.form.get('descripcio', ''),
    }

    # Llegir materials (ve com a JSON string)
    import json
    materials = json.loads(request.form.get('materials', '[]'))

    # Llegir fitxers
    fitxers = request.files.getlist('fitxers')

    nom   = client.get('nom', '(sense nom)')
    email = client.get('email', '')

    pdf = generar_pdf(client, materials)

    # Correu al client
    if email:
        msg_client = Message(
            subject='Sol·licitud rebuda - EngiLab',
            recipients=[email]
        )
        msg_client.body = f"""Hola {nom},

Hem rebut la teva sol·licitud correctament.
En breu l'equip d'EngiLab la revisarà i et notificarem la resolució.

Trobaràs el pressupost provisional adjunt a aquest correu.

Gràcies,
{NOM_EMPRESA}"""
        msg_client.attach('pressupost_provisional.pdf', 'application/pdf', pdf)

        # Adjuntar fitxers del projecte
        for f in fitxers:
            msg_client.attach(f.filename, f.content_type, f.read())

    # Correu a l'empresa
    msg_empresa = Message(
        subject=f'Nova sol·licitud de {nom}',
        recipients=[EMAIL_ENG],
        reply_to=email
    )
    msg_empresa.body = f"""Nova sol·licitud rebuda.

Nom:   {nom}
Email: {email}

Revisa el pressupost provisional adjunt."""
    msg_empresa.attach('pressupost_provisional.pdf', 'application/pdf', pdf)

    # Adjuntar fitxers també a l'empresa (reseteja el cursor)
    for f in fitxers:
        f.seek(0)
        msg_empresa.attach(f.filename, f.content_type, f.read())

    try:
        if email:
            mail.send(msg_client)
        mail.send(msg_empresa)
        return jsonify({'missatge': 'Sol·licitud enviada correctament!'})
    except Exception as e:
        app.logger.exception("Email send failed")
        return jsonify({'missatge': "No s'ha pogut enviar el correu ara mateix"}), 500

if __name__ == '__main__':
    app.run(debug=True)