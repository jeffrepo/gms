from odoo import models, fields
import paramiko
class Balanza(models.Model):
    _name = 'gms.balanza'
    _description = 'Balanza'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    follower_ids = fields.Many2many('res.users', string='Followers')


    name = fields.Char('Nombre', required=True)
    direccion_servidor = fields.Char('Dirección del Servidor', required=True)
    usuario = fields.Char('Usuario')
    contrasena = fields.Char('Contraseña')
