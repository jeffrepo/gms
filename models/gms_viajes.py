from odoo import models, fields, api, _
import datetime

class Viajes(models.Model):
    _name = 'gms.viaje'
    _description = 'Viaje'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    follower_ids = fields.Many2many('res.users', string='Followers')

    name = fields.Char(
    'Name', default=lambda self: _('New'),
    copy=False, readonly=True, tracking=True)

    agenda = fields.Many2one('gms.agenda', string='Agenda')
    fecha_viaje = fields.Date(string='Fecha de viaje', tracking="1")
    origen = fields.Many2one('res.partner', string='Origen', tracking="1")
    destino = fields.Many2one('res.partner', string='Destino', tracking="1")
    camion_disponible_id = fields.Many2one('gms.camiones.disponibilidad', string='Camión Disponible', tracking="1")
    camion_id = fields.Many2one('gms.camiones', string='Camion')
    conductor_id = fields.Many2one('res.partner', string='Chofer', compute="_compute_conductor_transportista")
    solicitante_id = fields.Many2one('res.partner', string='Solicitante')
    
    # nuevos campos 
    tipo_viaje = fields.Selection([('entrada', 'Entrada'), ('salida', 'Salida')], string="Tipo de Viaje")
    numero_remito = fields.Char(string="Número de remito / Guía")
    transportista_id = fields.Many2one('res.partner', string="Transportista", compute="_compute_conductor_transportista")
    ruta_id = fields.Many2one('gms.rutas', string="Ruta")
    albaran_id = fields.Many2one('stock.picking', string="Albarán")
    producto_transportado_id = fields.Many2one('product.product', string="Producto transportado")
    peso_bruto = fields.Float(string="Peso bruto")
    tara = fields.Float(string="Tara")
    peso_neto = fields.Float(string="Peso neto", compute="_compute_peso_neto")
    


    peso_neto_destino = fields.Float(string="Peso neto destino")
    peso_producto_seco = fields.Float(string="Peso producto seco")
    porcentaje_humedad_primer_muestra = fields.Float(string="Porcentaje humedad primer muestra")
    tolva = fields.Char(string="Tolva")
    silo = fields.Char(string="Silo")
    prelimpieza_entrada = fields.Selection([('si', 'Si'), ('no', 'No')], string="Prelimpieza entrada")
    secado_entrada = fields.Selection([('si', 'Si'), ('no', 'No')], string="Secado entrada")
    kilometros_flete = fields.Float(string="Kilómetros flete")
    kilogramos_a_liquidar = fields.Float(string="Kilogramos a liquidar")
    pedido_venta_id = fields.Many2one('sale.order', string="Pedido de venta")
    pedido_compra_id = fields.Many2one('purchase.order', string="Pedido de compra")
    observaciones = fields.Text(string="Observaciones")


    @api.onchange('camion_id')
    def _compute_conductor_transportista(self):
        for viaje in self:
            if viaje.camion_id:
                viaje.conductor_id = viaje.camion_id.conductor_id.id
                viaje.transportista_id = viaje.camion_id.transportista_id.id
                

    @api.depends('peso_bruto', 'tara')
    def _compute_peso_neto(self):
        for record in self:
            record.peso_neto = record.peso_bruto - record.tara



    @api.onchange('ruta_id')
    def _onchange_ruta_id(self):
         if self.ruta_id:   
             self.kilometros_flete = self.ruta_id.kilometros



    state = fields.Selection([
        ('cancelado', 'Cancelado'),
        ('borrador', 'Borrador'),
        ('coordinado', 'Coordinado'),
        ('proceso', 'Proceso'),
        ('terminado', 'Terminado'),
        ('liquidado', 'Liquidado')
    ], string='Estado', default='borrador', required=True)


    gastos_ids = fields.One2many('gms.gasto_viaje', 'viaje_id', string='Gastos')


    def action_proceso(self):
        self.write({'state': 'proceso'})


    def action_cancel(self):
        self.write({'state': 'cancelado'})

    def action_terminado(self):
        # Cambia el estado a 'terminado'
        self.write({'state': 'terminado'})

        # Guarda la fecha y hora actual
        fecha_hora_actual = fields.Datetime.now()

        # Busca el registro en gms.historial que tenga la misma agenda_id que el nombre del viaje
        historial = self.env['gms.historial'].search([('agenda_id.name', '=', self.name)], limit=1)

        if historial:
            # Actualiza la fecha_hora_liberacion en el registro existente
            historial.write({'fecha_hora_liberacion': fecha_hora_actual})

        # Recupera el camión asociado a este viaje (si existe)
        camion_id = self.camion_disponible_id.camion_id.id if self.camion_disponible_id else False

         # Actualiza el estado del camión a 'disponible' si existe
        self.camion_disponible_id.estado = "disponible"
        self.camion_disponible_id.fecha_hora_liberacion = fecha_hora_actual
        # if camion_id:
        #     camion_disponible = self.env['gms.camiones.disponibilidad'].search([('camion_id', '=', camion_id), ('estado', '=', 'ocupado')], limit=1)
        #     if camion_disponible:
        #         camion_disponible.write({
        #         'estado': 'disponible',
        #         'fecha_hora_liberacion': fecha_hora_actual,
        #     })
                
    def action_liquidado(self):
        self.write({'state': 'liquidado'})  
        
    def action_coordinado(self):
        self.write({'state': 'coordinado'})

    def action_borrador(self):
        self.write({'state': 'borrador'})

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gms.viaje')
        return super().create(vals)

