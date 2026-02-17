from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_regimen_fiscal = fields.Selection([
        ('601', '601 - General de Ley Personas Morales'),
        ('603', '603 - Personas Morales con Fines no Lucrativos'),
        ('605', '605 - Sueldos y Salarios'),
        ('606', '606 - Arrendamiento'),
        ('612', '612 - Personas Físicas con Actividades Empresariales'),
        ('621', '621 - Incorporación Fiscal'),
        ('626', '626 - Régimen Simplificado de Confianza'),
    ], string="Régimen Fiscal")

    x_uso_cfdi = fields.Selection([
        ('G01', 'G01 - Adquisición de mercancías'),
        ('G02', 'G02 - Devoluciones'),
        ('G03', 'G03 - Gastos en general'),
        ('I01', 'I01 - Construcciones'),
        ('I02', 'I02 - Mobiliario'),
        ('P01', 'P01 - Por definir'),
    ], string="Uso CFDI")
