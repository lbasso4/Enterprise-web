# Constants
Business_name = 'EngiLab'
Business_direction = 'ETSEIB: '
Business_cif = ''
Price_per_gram = ''
Price_per_hour = ''

# Costs computation
def compute_costs(weigth, g_price, hours, h_price, other):
    material_cost = weigth * g_price
    design_cost = hours * h_price
    total = material_cost + design_cost + other

    return {
        'material': material_cost,
        'design': coste_diseno,
        'total': total,
    }

#Create a pdf
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from datetime import datetime
import os

def gen_budget(num_budget, user_data, costs):
    if not os.path.exists("budgets"):
        os.makedirs("budgets")
filename = f'budgets/budget_{num_budget}.pdf'
doc = SimpleDocTemplate(filename)
elements = []
styles = getSampleStyleSheet()

elements.append(Paragraph(f"<b>{Business_name}</b>", styles["Title"]))
elements.append(Spacer(1, 0.5*cm))

elements.append(Paragraph(, styles["Normal"]))
elements.append(Paragraph(f"CIF: {Business_cif}", styles["Normal"]))
elements.append(Spacer(1, 0.5*cm))

elements.append(Paragraph(f"<b>Factura Nº:</b> {numero_factura}", styles["Normal"]))
elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", styles["Normal"]))
elements.append(Spacer(1, 0.5*cm))

elements.append(Paragraph(f"<b>Cliente:</b> {cliente_data['nombre']}", styles["Normal"]))
elements.append(Paragraph(f"NIF: {cliente_data['nif']}", styles["Normal"]))
elements.append(Paragraph(f"Dirección: {cliente_data['direccion']}", styles["Normal"]))
elements.append(Spacer(1, 1*cm))

