from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from datetime import datetime, timedelta
# import pdb; pdb.set_trace()
import json


_logger = logging.getLogger(__name__)

class Agenda(models.Model):
    _name = 'gms.agenda'
    _description = 'Agenda'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"
    name = fields.Char(
    'Name', )


    # def _get_warehouse_partner_domain(self):
    #     # Asegura que hay un solicitante_id definido
    #     # if not self.solicitante_id:
    #     #     return [('id', '=', False)]  # Devuelve un dominio vacío si no hay solicitante

    #     # Busca todos los subcontactos (hijos) del solicitante que sean de tipo 'planta' o 'chacra'
    #     logging.warning(self.solicitante_id)
    #     logging.warning(self)
    #     id = self.env.context.get('active_ids', [])
    #     logging.warning(id)
    #     subcontactos = self.env['res.partner'].search([
    #         ('parent_id', '=', self.solicitante_id.id),
    #         ('tipo', 'in', ['planta', 'chacra']),
    #     ])
    #     logging.warning(subcontactos)
    #     logging.warning('_get_warehouse_partner_domain')
    #     # Devuelve un dominio que incluya solo esos subcontactos
    #     return [('id', 'in', subcontactos.ids)]
    
    name = fields.Char(required=True, default=lambda self: _('New'), copy=False, readonly=True, tracking=True)

    fecha = fields.Date(string='Fecha', required=True, readonly=True, tracking="1", default=fields.Date.today())

    fecha_viaje = fields.Date(string='Fecha de viaje', required=True, tracking="1")

    origen = fields.Many2one('res.partner', 
                             string='Origen', 
                             required=True, 
                             readonly=True,
                             tracking="1", 
                             ondelete='cascade',context="{'default_parent_id': solicitante_id}") 
    

    
    destino = fields.Many2one('res.partner', 
                              string='Destino', 
                              required=True, 
                              tracking="1", 
                              )
    
    transportista_id = fields.Many2one('res.partner', 
                                       string='Trasportista', 
                                       readonly=True,
                                       states={'proceso': [('readonly', False), ('required', True)],
                                           'cancelado': [('readonly', True)]},
                                       
                                       tracking="1")
    
    camion_disponible_id = fields.Many2one('gms.camiones.disponibilidad',
                                           string='Disponibilidad Camión',
                                           states={'proceso': [('readonly', False), ('required', True)],
                                           'cancelado': [('readonly', True)]},
                                           tracking="1",
                                           domain="[('estado', '=', 'disponible'), ('camion_id.disponible_zafra', '=', True)]",
                                           attrs="{'invisible': [('state', '=', 'solicitud')]}")  
    

    camion_id = fields.Many2one('gms.camiones', string='Camion', states={'proceso': [('readonly', False), ('required', True)],
                                           'cancelado': [('readonly', True)]}, readonly=True ,  tracking="1")

    conductor_id = fields.Many2one('res.partner', string='Chofer',  states={'proceso': [('readonly', False), ('required', True)],
                                           'cancelado': [('readonly', True)]}, readonly=True,  tracking="1")

    solicitante_id = fields.Many2one('res.partner', 
                                     string='Solicitante', 
                                     store=True,
                                     readonly=True, 
                                     tracking="1", 
                                     domain="[('tipo', '!=', 'chacras'), ('tipo', '!=', 'planta'), ('tipo', '=', False)]")

    viaje_count = fields.Integer(string="Número de viajes", compute="_compute_viaje_count", tracking="1")

    picking_id = fields.Many2one('stock.picking', string='Stock Picking', required=True, readonly=True, tracking=True)

    tipo_viaje = fields.Selection([('entrada', 'Entrada'), ('salida', 'Salida')], string="Tipo de Viaje", readonly=True, tracking="1")

    albaran_id = fields.Many2one('stock.picking', string="Albarán", compute="_compute_albaran", store=True, readonly=True , tracking=True)

    order_id = fields.Many2one('purchase.order', string='Orden de Compra', tracking=True)
    
     # Campos calculados para dominios en formato JSON
    origen_domain = fields.Char(compute='_compute_origen_domain', readonly=True, store=False)
    destino_domain = fields.Char(compute='_compute_destino_domain', readonly=True, store=False)

    @api.depends('solicitante_id', 'tipo_viaje', 'fecha_viaje')  # Asegúrate de incluir todas las dependencias relevantes
    def _compute_origen_domain(self):
        for record in self:
            domain = [('id', '=', False)]  # Un dominio que inicialmente no permite seleccionar ningún registro
            if record.tipo_viaje == 'entrada' and record.solicitante_id:
                domain = [('parent_id', '=', record.solicitante_id.id), ('id', '!=', record.solicitante_id.id)]
            elif record.tipo_viaje == 'salida':
                # Aquí va la lógica para definir el dominio de origen cuando el tipo de viaje es 'salida'
                pass
            record.origen_domain = json.dumps(domain)

    @api.depends('solicitante_id', 'tipo_viaje', 'fecha_viaje')  # Ajusta las dependencias según sea necesario
    def _compute_destino_domain(self):
        for record in self:
            domain = [('id', '=', False)]  # Un dominio inicial
            if record.tipo_viaje == 'salida' and record.solicitante_id:
                domain = [('parent_id', '=', record.solicitante_id.id), ('tipo', 'in', ['planta', 'chacra'])]
            elif record.tipo_viaje == 'entrada':
                # Aquí va la lógica para definir el dominio de destino cuando el tipo de viaje es 'entrada'
                # Esto podría incluir la lógica para `picking_type_id.warehouse_id.partner_id.id` mencionada anteriormente
                pass
            record.destino_domain = json.dumps(domain)

    




    @api.depends('name')
    def _compute_albaran(self):
        for record in self:
            viaje = self.env['gms.viaje'].search([('agenda', '=', record.id)], limit=1)
            if viaje:
                record.albaran_id = viaje.albaran_id


    


    @api.depends('name') 
    def _compute_viaje_count(self):
        for record in self:
            record.viaje_count = self.env['gms.viaje'].search_count([('agenda', '=', record.id)])



    state = fields.Selection([
        ('solicitud', 'Solicitud'),
        ('proceso', 'Proceso'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado')
    ], string='Estado', default='solicitud', required=True, tracking=True)

    follower_ids = fields.Many2many('res.users', string='Followers')





    @api.onchange('camion_disponible_id')
    def _onchange_camion_disponible_id(self):
        if self.camion_disponible_id:
            self.transportista_id = self.camion_disponible_id.camion_id.transportista_id.id
            self.conductor_id = self.camion_disponible_id.camion_id.conductor_id.id
            self.camion_id = self.camion_disponible_id.camion_id.id
            

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            solicitante_id = vals.get('solicitante_id')

            if vals.get('tipo_viaje') == 'entrada' and solicitante_id:
                # Para viajes de tipo 'entrada', buscar el primer subcontacto del solicitante
                primer_subcontacto = self.env['res.partner'].search([
                    ('parent_id', '=', solicitante_id),
                    ('id', '!=', solicitante_id)
                ], limit=1, order='id')
                if primer_subcontacto:
                    vals['origen'] = primer_subcontacto.id
                    _logger.info(f"Estableciendo origen a primer subcontacto {primer_subcontacto.name} para viaje de entrada.")

            elif vals.get('tipo_viaje') == 'salida' and solicitante_id:
                # Para viajes de tipo 'salida', buscar un subcontacto adecuado para el destino
                primer_subcontacto = self.env['res.partner'].search([
                    ('parent_id', '=', solicitante_id),
                    ('tipo', 'in', ['planta', 'chacra']),
                ], limit=1)
                if primer_subcontacto:
                    vals['destino'] = primer_subcontacto.id
                    _logger.info(f"Estableciendo destino a primer subcontacto {primer_subcontacto.name} de tipo 'planta' o 'chacra' para viaje de salida.")
                else:
                    _logger.warning("No se encontró un subcontacto adecuado de tipo 'planta' o 'chacra' para el destino en viaje de salida.")

            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('gms.agenda')

        return super().create(vals_list)

    

    
    def action_cancel(self):
        self.write({'state': 'cancelado'})

    def action_proceso(self):
        self.write({'state': 'proceso'})

    def action_view_scheduled_trips(self):
        self.ensure_one()  # 
        viaje = self.env['gms.viaje'].search([('agenda', '=', self.id)], limit=1)
        if viaje:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'gms.viaje',
                'view_mode': 'form',
                'res_id': viaje.id,
                'target': 'current',
            }
        else:
            raise UserError('No hay un viaje asociado a esta agenda.')

    def _check_fecha_viaje(self):
        for agenda in self:
            if agenda.fecha_viaje:
                fecha_viaje = fields.Date.from_string(agenda.fecha_viaje)
                fecha_actual = fields.Date.from_string(fields.Date.today())
                dias_diferencia = (fecha_viaje - fecha_actual).days
                if dias_diferencia > 1:
                    raise UserError("No se puede confirmar: La fecha de viaje es mayor a 1 día desde la fecha actual.")

    def action_confirm(self):
        
         # Enviar notificaciones por SMS
        self.enviar_notificaciones_sms()
       
        self._check_fecha_viaje()
        
        if self.camion_disponible_id:
            self.camion_disponible_id.write({'estado': 'ocupado'})

      
        if len(self.picking_id.move_ids_without_package) > 0:
            producto_transportado_id = self.picking_id.move_ids_without_package[0].product_id.id
            cantidad = self.picking_id.move_ids_without_package[0].quantity_done

        else:
            producto_transportado_id = False
            cantidad = 0.0


        _logger.info("Producto transportado ID: %s", producto_transportado_id)
        _logger.info("Cantidad: %s", cantidad)

        # Obtener el albarán asociado
        albaran = self.env['stock.picking'].browse(self.picking_id.id)

        # Asegurarse de que el albarán existe y tiene un destino
        if albaran and albaran.location_dest_id:
            silo_id = albaran.location_dest_id.id
        else:
            silo_id = None 

       
        # Llenar el registro gms.viaje
        dic_viaje = {
            'agenda': self.id,
            'fecha_viaje': self.fecha_viaje,
            'origen': self.origen.id,
            'destino': self.destino.id,
            'camion_disponible_id': self.camion_disponible_id.id,
            'camion_id': self.camion_disponible_id.camion_id.id,  
            'conductor_id': self.camion_disponible_id.conductor_id.id,
            'solicitante_id': self.solicitante_id.id,
            'tipo_viaje': self.tipo_viaje,
            'transportista_id': self.transportista_id.id,    
            'state': 'proceso',
            'producto_transportado_id': producto_transportado_id,
            'albaran_id': self.picking_id.id,
            'kilogramos_a_liquidar': cantidad,
            'arribo': fields.Datetime.now(),
            'silo_id': silo_id
        }
        if self.tipo_viaje == "entrada":
            dic_viaje['pedido_compra_id'] = self.picking_id.purchase_id.id

        if self.tipo_viaje == "salida":
            dic_viaje["pedido_venta_id"] = self.picking_id.sale_id.id

        # Buscar una ruta que coincida con el origen y destino del viaje
        ruta = self.env['gms.rutas'].search([
            ('direccion_origen_id', '=', dic_viaje['origen']),
            ('direccion_destino_id', '=', dic_viaje['destino'])
        ], limit=1)

        # Si se encuentra una ruta, asignarla al diccionario antes de crear el viaje
        if ruta:
            dic_viaje['ruta_id'] = ruta.id

        viaje = self.env['gms.viaje'].create(dic_viaje)

        if self.tipo_viaje == 'entrada' and self.picking_id.purchase_id:
            self.picking_id.purchase_id.viaje_ids += viaje
        elif self.tipo_viaje == 'salida' and self.picking_id.sale_id:
            self.picking_id.sale_id.viaje_ids += viaje

        if self.camion_disponible_id:
            self.env['gms.historial'].create({
                'fecha': self.fecha,
                'camion_id': self.camion_disponible_id.camion_id.id,
                'agenda_id': self.id,
            })

        self.write({'state': 'confirmado'})
        



    def unlink(self):
        for record in self:
            if record.state in ['proceso', 'confirmado', 'cancelado']:
                raise UserError(_('No puedes eliminar una agenda en el estado %s.') % record.state)
        return super(Agenda, self).unlink()
    

    @api.onchange('origen', 'destino')
    def _check_origen_destino(self):
        if self.origen and self.destino and self.origen == self.destino:
            raise UserError("Origen y Destino no pueden ser iguales.")
        


    #ver albaran asociado 
    def action_view_picking(self):
        self.ensure_one()
        if self.albaran_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_mode': 'form',
                'res_id': self.albaran_id.id,
                'target': 'current',
            }
        else:
            raise UserError(_('No hay un albarán asociado a esta agenda.'))
        




   
   

    # @api.onchange('tipo_viaje')
    # def _onchange_tipo_viaje(self):
    #     # Si el tipo de viaje es 'salida', ajustar el dominio del campo destino
    #     if self.tipo_viaje == 'salida':
    #         return {'domain': {'destino': [('tipo', 'in', ['puerto', 'planta'])]}}
    #     else:
    #         # Restablecer el dominio original para otros tipos de viaje
    #         return {'domain': {'destino': self._get_warehouse_partner_domain()}}


    def enviar_notificaciones_sms(self):
        _logger.info("Iniciando envío de notificaciones SMS para la agenda %s", self.name)

        # Notificación al Camionero
        if self.camion_disponible_id and self.camion_disponible_id.conductor_id:
            mensaje_camionero = "Detalles de la agenda: {} - Origen: {} - Destino: {} - Link Origen: {} - Link Destino: {}".format(
                self.name,
                self.origen.display_name if self.origen else '',
                self.destino.display_name if self.destino else '',
                self.origen.link if self.origen and self.origen.link else 'No disponible',
                self.destino.link if self.destino and self.destino.link else 'No disponible'
            )
            telefono_camionero = self.camion_disponible_id.conductor_id.mobile
            if telefono_camionero:
                _logger.info("Enviando SMS al camionero: %s", telefono_camionero)
                try:
                    self.env['sms.sms'].create({
                        'number': telefono_camionero,
                        'body': mensaje_camionero
                    }).send()
                    self.message_post(body=f"SMS enviado al camionero ({telefono_camionero}): {mensaje_camionero}")
                except Exception as e:
                    _logger.error("Error al enviar SMS al camionero: %s", e)
                    self.message_post(body=f"Error al enviar SMS al camionero ({telefono_camionero}): {e}")
            else:
                mensaje_error = f"No se pudo enviar SMS al camionero {self.camion_disponible_id.conductor_id.name} porque no hay número de teléfono móvil disponible"
                _logger.warning(mensaje_error)
                self.message_post(body=mensaje_error)

    
        # Notificación al Solicitante
        if self.solicitante_id:
            mensaje_solicitante = "Detalles de la agenda: {} - Matricula: {}  - Origen: {} - Destino: {} - Link Origen: {} - Link Destino: {}".format(
                self.name,
                self.camion_id.matricula if self.camion_id else "-",
                self.origen.name if self.origen else "-",
                self.destino.name if self.destino else "-",
                self.origen.link if self.origen and self.origen.link else "No disponible",
                self.destino.link if self.destino and self.destino.link else "https://www.google.com/maps"
            )
            telefono_solicitante = self.solicitante_id.mobile or self.solicitante_id.phone
            if telefono_solicitante:
                _logger.info("Enviando SMS al solicitante: %s", telefono_solicitante)
                try:
                    self.env['sms.sms'].create({
                        'number': telefono_solicitante,
                        'body': mensaje_solicitante
                    }).send()
                    self.message_post(body=f"SMS enviado al solicitante ({telefono_solicitante}): {mensaje_solicitante}")
                except Exception as e:
                    _logger.error("Error al enviar SMS al solicitante: %s", e)
                    self.message_post(body=f"Error al enviar SMS al solicitante ({telefono_solicitante}): {e}")
            else:
                mensaje_error = "No se pudo enviar SMS al solicitante: no hay número de teléfono disponible"
                _logger.warning(mensaje_error)
                self.message_post(body=mensaje_error)
    
        _logger.info("Finalizado el envío de notificaciones SMS para la agenda %s", self.name)



    