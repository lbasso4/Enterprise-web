# Constants
Nom_Negoci = 'EngiLab'
Direcció_Negoci= 'ETSEIB: '
CIF_Negoci = ''
Preu_gram = ''
Preu_hora = ''

# Costs computation
def compute_costs(pes, Preu_gram, hores, Preu_hora, altres):
    cost_material = pes * Preu_gram
    cost_disseny = hores * Preu_hora
    total = cost_material + cost_disseny + altres

    return {
        'material': cost_material,
        'disseny': cost_disseny,
        'total': total,
    }

#Create a pdf
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from datetime import datetime
import os

def gen_budget(num_factura, dades_client, costos):
    if not os.path.exists("factures"):
        os.makedirs("factures")
filename = f'budgets/budget_{num_factura}.pdf'
doc = SimpleDocTemplate(filename)
elements = []
styles = getSampleStyleSheet()

elements.append(Paragraph(f"<b>{Nom_negoci}</b>", styles["Title"]))
elements.append(Spacer(1, 0.5*cm))

elements.append(Paragraph(, styles["Normal"]))
elements.append(Paragraph(f"CIF: {CIF_negoci}", styles["Normal"]))
elements.append(Spacer(1, 0.5*cm))

elements.append(Paragraph(f"<b>Factura Nº:</b> {num_factura}", styles["Normal"]))
elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", styles["Normal"]))
elements.append(Spacer(1, 0.5*cm))

elements.append(Paragraph(f"<b>User:</b> {dades_client['nombre']}", styles["Normal"]))
elements.append(Paragraph(f"NIF: {dades_client['nif']}", styles["Normal"]))
elements.append(Paragraph(f"Direction: {dades_client['direccion']}", styles["Normal"]))
elements.append(Spacer(1, 1*cm))

data = [["Concepte", "Import (€)"],
    ["Material impressió 3D", f"{costos['material']:.2f}"],
    ["Diseny i fabricació", f"{costs['disseny']:.2f}"],
    ["Total", f"{costs['total']:.2f}"]]

table = Table(data, colWidths=[10*cm, 4*cm])
table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.black),
    ('TEXTCOLOR',(0,0),(-1,0),colors.white),
    ('ALIGN',(1,1),(-1,-1),'RIGHT'),
    ('GRID', (0,0), (-1,-1), 1, colors.grey),
    ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey)]))

elements.append(table)

doc.build(elements)
