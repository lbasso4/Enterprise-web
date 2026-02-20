# Constants
Business_name = 'EngiLab'
Business_direction = 'ETSEIB: '
Business_cif = ''
Price_per_gram = ''
Price_per_hour = ''

# Costs c
def compute_costs(weigth, g_price, hours, h_price, other):
    material_cost = weigth * g_price
    design_cost = hours * h_price
    total = material_cost + design_cost + other

    return {
        'material': material_cost,
        'design': coste_diseno,
        'total': total,
    }
