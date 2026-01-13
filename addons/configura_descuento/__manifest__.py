# configura_descuento/__manifest__.py
{
    'name': "Configura Descuento Máximo",
    'summary': "Establece un límite de descuento por producto en cotizaciones.",
    'description': """
        Este módulo permite:
        1. Definir un porcentaje máximo de descuento en la ficha del producto.
        2. Validar y bloquear en la línea de cotización si se excede ese límite.
        3. Mostrar el límite permitido visualmente en la orden de venta.
    """,
    'author': "Maharba112",
    'version': '1.0',
    'depends': ['base', 'sale', 'product'],
    'data': [
        'views/views.xml',
        'views/product_views.xml'
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}