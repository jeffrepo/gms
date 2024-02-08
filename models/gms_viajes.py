from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import paramiko
import logging
import requests
import asyncio
from asyncvnc import Client
import serial
_logger = logging.getLogger(__name__)


class Viajes(models.Model):
    _name = 'gms.viaje'
    _description = 'Viaje'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    follower_ids = fields.Many2many('res.users', string='Followers')

    name = fields.Char(
    'Name', default=lambda self: _('New'),
    copy=False, readonly=True, tracking=True)

    agenda = fields.Many2one('gms.agenda', string='Agenda', tracking="1" )

    agenda_count = fields.Integer(string="Número de Agendas", compute="_compute_agenda_count")

    @api.depends('agenda')
    def _compute_agenda_count(self):
        for record in self:
            record.agenda_count = 1 if record.agenda else 0

    def action_view_agenda(self):
        self.ensure_one() 
        if self.agenda:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'gms.agenda',
                'view_mode': 'form',
                'res_id': self.agenda.id,
                'target': 'current',
            }
        else:
            raise UserError('No hay una agenda asociada a este viaje.')

    fecha_viaje = fields.Date(string='Fecha de viaje', tracking="1")

    origen = fields.Many2one('res.partner', 
                             string='Origen', 
                             tracking="1", 
                            domain="[('tipo', 'in', ['planta', 'chacra', 'puerto']), ('parent_id', '=', solicitante_id)]"
    )
    destino = fields.Many2one('res.partner', string='Destino', tracking="1")

    camion_disponible_id = fields.Many2one('gms.camiones.disponibilidad', string='Camión Disponible', tracking="1")

    camion_id = fields.Many2one('gms.camiones', string='Camion', tracking="1")

    conductor_id = fields.Many2one('res.partner', string='Chofer', compute="_compute_conductor_transportista", tracking="1")

    solicitante_id = fields.Many2one('res.partner', string='Solicitante', tracking="1",
                                 domain="[('tipo', 'not in', ['chacra', 'planta'])]")
    
    # nuevos campos 
    tipo_viaje = fields.Selection([('entrada', 'Entrada'), ('salida', 'Salida')], string="Tipo de Viaje", tracking="1")

    numero_remito = fields.Char(string="Número de remito / Guía", tracking="1")
    
    transportista_id = fields.Many2one('res.partner', string="Transportista", compute="_compute_conductor_transportista", tracking="1")

    ruta_id = fields.Many2one('gms.rutas', 
                          string="Ruta", 
                          domain="[('direccion_origen_id', '=', origen),('direccion_destino_id', '=', destino)]",
                          tracking="1")
    

   
    
    

    albaran_id = fields.Many2one('stock.picking', string="Albarán", tracking="1")

    producto_transportado_id = fields.Many2one('product.product', string="Producto transportado", readonly=True, tracking="1")

    peso_bruto = fields.Float(string="Peso bruto", tracking="1")

    tara = fields.Float(string="Tara", tracking="1")

    peso_neto = fields.Float(string="Peso neto", readonly=True, compute="_compute_peso_neto", tracking="1",store=True)
    
    estado = fields.Char(string = "s" , tracking=True)

    peso_neto_destino = fields.Float(string="Peso neto destino", tracking="1")

    peso_producto_seco = fields.Float(string="Peso producto seco", tracking="1" , readonly=True)

    porcentaje_humedad_primer_muestra = fields.Float(string="Porcentaje humedad primer muestra", tracking="1")

    tolva_id = fields.Many2one('gms.tolva', string='Tolva', tracking="1")

    silo_id = fields.Many2one('stock.location', string="Silio", domain=[('usage', '=', 'internal')], tracking="1")

    prelimpieza_entrada = fields.Boolean(string="Prelimpieza Entrada", tracking=True)
    secado_entrada = fields.Boolean(string="Secado Entrada", tracking=True)

    kilometros_flete = fields.Float(string="Kilómetros flete", tracking="1")

    kilogramos_a_liquidar = fields.Float(string="Kilogramos a liquidar" , readonly=True, compute="_compute_kilogramos_a_liquidar", store=True, tracking=True)

    pedido_venta_id = fields.Many2one('sale.order', string="Pedido de venta", tracking="1", readonly=True)

    pedido_compra_id = fields.Many2one('purchase.order', string="Pedido de compra", tracking="1", readonly=True)

    observaciones = fields.Text(string="Observaciones", tracking="1")

    albaran_count = fields.Integer(string="Número de Albaranes", compute="_compute_albaran_count" , tracking=True)

    albaran_id = fields.Many2one('stock.picking', string="Albarán" , tracking=True)

    purchase_order_id= fields.Many2one('purchase.order', tracking=True)

    medidas_propiedades_ids = fields.One2many('gms.medida.propiedad', 'viaje_id', string='Medidas de Propiedades', tracking="1")

    arribo = fields.Datetime(string="Arribo", tracking=True)
    partida = fields.Datetime(string="Partida", tracking=True)

    chacra = fields.Char(string='Chacra', tracking="1")
    remito = fields.Char(string='Remito', tracking="1")

    firma = fields.Binary(string='Firma', tracking="1")

    sale_order_id = fields.Many2one('sale.order', string='Orden de Venta' , tracking=True)
    purchase_order_id = fields.Many2one('purchase.order', string='Orden de Compra' , tracking=True)

    balanza_id = fields.Many2one('gms.balanza', string='Balanza' , tracking=True)
    
    humedad = fields.Float(string='Humedad' , tracking=True)
    
    ph = fields.Float(string='PH' , tracking=True)
    
    proteina = fields.Float(string='Proteína'  , tracking=True)
    
    factura_id = fields.Many2one('account.move', string='Factura Asociada')

    picking_id = fields.Many2one('stock.picking', string='Albarán')

    creado_desde_albaran = fields.Boolean(string='Creado desde Albarán', default=False)

    mensaje_enviado = fields.Boolean(string='Mensaje Enviado', default=False)

    # prelimpieza_entrada_1 = fields.Selection([('si', 'Si'), ('no', 'No')], string="Prelimpieza entrada", tracking="1")

    # secado_entrada_1 = fields.Selection([('si', 'Si'), ('no', 'No')], string="Secado entrada", tracking="1")

    
    

    def _compute_albaran_count(self):
        for record in self:
            record.albaran_count = 1 if record.albaran_id else 0



    @api.onchange('camion_id')
    def _compute_conductor_transportista(self):
        for viaje in self:
            if viaje.camion_id:
                viaje.conductor_id = viaje.camion_id.conductor_id.id
                viaje.transportista_id = viaje.camion_id.transportista_id.id
            else:
                # Limpia los campos si no hay camion_id
                viaje.conductor_id = None
                viaje.transportista_id = None

                

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
        ('coordinado', 'Coordinado'),
        ('proceso', 'Proceso'),
        ('terminado', 'Terminado'),
        ('liquidado', 'Liquidado')
    ], string='Estado', default='coordinado', required=True)


    gastos_ids = fields.One2many('gms.gasto_viaje', 'viaje_id', string='Gastos' , tracking=True)


    def action_proceso(self):
        # Eliminar gastos de viaje existentes
        gastos_viaje = self.env['gms.gasto_viaje'].search([('viaje_id', '=', self.id)])
        gastos_viaje.unlink()  # Esto eliminará todos los gastos asociados al viaje actual

        self.write({'state': 'proceso'})


    def action_cancel(self):
        self.write({'state': 'cancelado'})

        if self.camion_disponible_id:
            self.camion_disponible_id.write({'estado': 'disponible'})

        return True

    def action_terminado(self):
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


        fecha_hora_actual = fields.Datetime.now()
            # Establece la fecha y hora de partida para el viaje
        self.partida = fecha_hora_actual

        
        if self.tipo_viaje == 'entrada':
            self.enviar_sms_solicitante()

       
        if self.tipo_viaje in ['entrada', 'salida']:
            # Obtener los productos de configuración
            config = self.env['res.config.settings'].default_get([])
            producto_secado_id = config.get('producto_secado_id')
            producto_pre_limpieza_id = config.get('producto_pre_limpieza_id')
            producto_flete_puerto_id = config.get('producto_flete_puerto_id')
    
            # Obtener la moneda de compra del proveedor
            moneda_proveedor_id = self.transportista_id.property_purchase_currency_id.id 
            
            # Obtener el valor de medida para humedad
            valor_medida = 0  
            for medida in self.medidas_propiedades_ids:
                valor_medida = medida.valor_medida  
        
            # Buscar la coincidencia en gms.datos_humedad para calcular el precio total del secado
            datos_humedad = self.env['gms.datos_humedad'].search([('humedad', '=', valor_medida)], limit=1)
            tarifa_humedad = datos_humedad.tarifa if datos_humedad else 0  
            precio_total_secado = (tarifa_humedad/1000) * self.peso_neto if tarifa_humedad else 0
    
            # Para el producto de Pre Limpieza
            producto_pre_limpieza = self.env['product.product'].browse(producto_pre_limpieza_id)
            precio_total_pre_limpieza = self.peso_neto * producto_pre_limpieza.lst_price if producto_pre_limpieza else 0
    
            # Obtener el valor de kilometros_flete para calcular el precio total del flete puerto
            kilometros_flete = self.kilometros_flete 

            # Obtener el valor de 'cantidad_kilos_flete_puerto' de la configuración
            config_params = self.env['ir.config_parameter'].sudo()
            cantidad_kilos_flete_puerto = float(config_params.get_param('gms.cantidad_kilos_flete_puerto', 0.0))
        
            # Buscar coincidencia en gms.datos_flete
            datos_flete = self.env['gms.datos_flete'].search([('flete_km', '=', kilometros_flete)], limit=1)
            tarifa_flete = datos_flete.tarifa if datos_flete else 0  
        
            # Calcular el precio_total_flete para 'Flete Puerto'
            precio_total_flete_puerto = cantidad_kilos_flete_puerto * self.kilometros_flete
    
            # Crear las líneas de gasto si los productos están configurados
            if producto_secado_id:
                self.env['gms.gasto_viaje'].create({
                    'name': 'Secado',
                    'producto_id': producto_secado_id,
                    'precio_total': precio_total_secado, 
                    'viaje_id': self.id,
                    'estado_compra': 'no_comprado',
                    'moneda_id': moneda_proveedor_id
                })
    
            if producto_pre_limpieza_id:
                self.env['gms.gasto_viaje'].create({
                    'name': 'Pre Limpieza',
                    'producto_id': producto_pre_limpieza_id,
                    'precio_total': precio_total_pre_limpieza,  
                    'viaje_id': self.id,
                    'estado_compra': 'no_comprado',
                    'moneda_id': moneda_proveedor_id
                })
    
            if producto_flete_puerto_id:
                self.env['gms.gasto_viaje'].create({
                    'name': 'Flete Puerto',
                    'producto_id': producto_flete_puerto_id,
                    'precio_total': precio_total_flete_puerto,  
                    'viaje_id': self.id,
                    'estado_compra': 'no_comprado',
                    'moneda_id': moneda_proveedor_id
                })

       


                
    def action_liquidado(self):
        Invoice = self.env['account.move']
        for viaje in self:
            if viaje.albaran_id and viaje.albaran_id.state != 'done':
                raise UserError("No se puede pasar el viaje a estado 'Liquidado' hasta que el albarán esté confirmado.")
            else:
                # Sumar el total de los gastos
                total_gastos = sum(gasto.precio_total for gasto in viaje.gastos_ids)
    
                # Preparar las líneas de la factura
                invoice_lines = []
                if viaje.tipo_viaje == 'entrada':
                    for line in viaje.purchase_order_id.order_line:
                        invoice_lines.append((0, 0, {
                            'product_id': line.product_id.id,
                            'quantity': line.product_qty,
                            'price_unit': line.price_unit,
                            
                        }))
                else: 
                    for line in viaje.sale_order_id.order_line:
                        invoice_lines.append((0, 0, {
                            'product_id': line.product_id.id,
                            'quantity': line.product_uom_qty,
                            'price_unit': line.price_unit,
                            
                        }))

                # Fecha actual para la factura
                fecha_actual = fields.Date.today()
        
                # Preparar valores para la factura
                invoice_vals = {
                    'partner_id': viaje.transportista_id.id if viaje.tipo_viaje == 'entrada' else viaje.solicitante_id.id,
                    'move_type': 'in_invoice' if viaje.tipo_viaje == 'entrada' else 'out_invoice',
                    'invoice_line_ids': invoice_lines,
                    'total_descontar': str(total_gastos),
                    'invoice_date': fecha_actual,
                    
                }
        
                # Agregar el ID del viaje actual a los valores de la factura
                invoice_vals['viajes_ids'] = [(4, viaje.id)]
        
                # Crear la factura
                if total_gastos > 0:
                    factura_creada = Invoice.create(invoice_vals)
                    viaje.write({'factura_id': factura_creada.id})
        
                viaje.write({'state': 'liquidado'})
        
        
    def action_coordinado(self):
        self.write({'state': 'coordinado'})

    def action_borrador(self):
        self.write({'state': 'borrador'})


       


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
            raise UserError('No hay un albarán asociado a este viaje.')
    


    def action_generate_purchase_order(self):
        PurchaseOrder = self.env['purchase.order']

        # Agrupa los viajes por transportista
        grouped_trips_by_transportista = {}
        for trip in self:
            if trip.transportista_id not in grouped_trips_by_transportista:
                grouped_trips_by_transportista[trip.transportista_id] = []
            grouped_trips_by_transportista[trip.transportista_id].append(trip)

        # Por cada transportista, crea una orden de compra
        for transportista, trips in grouped_trips_by_transportista.items():
            po_vals = {
                'partner_id': transportista.id,
                'order_line': [],
            }

            # Guarda una relación entre gastos y líneas de compra
            gastos_and_po_lines = {}

            for trip in trips:
                for gasto in trip.gastos_ids:
                    if gasto.estado_compra == 'no_comprado':
                        po_line_vals = {
                            'product_id': gasto.producto_id.id,
                            'name': gasto.name or gasto.producto_id.name,
                            'product_qty': 1,
                            'price_unit': gasto.precio_total,
                            'product_uom': gasto.producto_id.uom_id.id,
                            'date_planned': fields.Date.today(),
                        }
                        po_vals['order_line'].append((0, 0, po_line_vals))
                        # Asociar el gasto con esta línea de orden de compra
                        gastos_and_po_lines[gasto] = po_line_vals

            if po_vals['order_line']:
                purchase_order = PurchaseOrder.create(po_vals)
                for trip in trips:
                    for gasto in trip.gastos_ids:
                        if gasto.estado_compra == 'no_comprado':
                            gasto.write({
                                'purchase_order_id': purchase_order.id,
                                'estado_compra': 'comprado'
                            })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }



    



    @api.onchange('kilogramos_a_liquidar')
    def _onchange_kilogramos_a_liquidar(self):
        if self.albaran_id:
            # Verifica si hay líneas de albarán antes de intentar acceder a ellas
            if self.albaran_id.move_ids_without_package:
                # Obtener la primera línea del albarán (esto podría cambiar si hay múltiples líneas)
                move_line = self.albaran_id.move_ids_without_package[0]
                # Actualizar la demanda (quantity_done) de esa línea
                move_line.write({
                    'quantity_done': self.kilogramos_a_liquidar
                })
            else:
                
                pass
        # No se lanza error si no hay albarán asociado

        




   
    @api.depends('peso_neto', 'medidas_propiedades_ids.merma_kg')
    def _compute_kilogramos_a_liquidar(self):
        for record in self:
            _logger.info("Calculando kilogramos a liquidar para el viaje %s", record.name)
            _logger.info("Peso Neto: %s", record.peso_neto)
            
            total_mermas = sum(record.medidas_propiedades_ids.mapped('merma_kg'))
            _logger.info("Total Mermas: %s", total_mermas)
            
            record.kilogramos_a_liquidar = record.peso_neto - total_mermas
            _logger.info("Kilogramos a Liquidar Calculados: %s", record.kilogramos_a_liquidar)





    @api.onchange('ruta_id')
    def _onchange_ruta_id(self):
        # Encuentra y elimina la línea antigua si existe
        gastos_a_eliminar = self.gastos_ids.filtered(lambda g: g.es_de_ruta)
        self.gastos_ids -= gastos_a_eliminar

        if self.ruta_id:
           
            pass


 



    
    @api.model
    def _post_create_actions(self, vals):
        if vals.get('ruta_id'):
            ruta = self.env['gms.rutas'].browse(vals['ruta_id'])
            if ruta.direccion_origen_id.id != vals.get('origen') or ruta.direccion_destino_id.id != vals.get('destino'):
                raise UserError("El origen y destino de la ruta deben ser iguales al del viaje.")
        return super(Viajes, self).create(vals)

    def write(self, vals):
        # Si se actualiza la ruta, verificar que coincida con el origen y destino del viaje.
        if vals.get('ruta_id'):
            ruta = self.env['gms.rutas'].browse(vals['ruta_id'])
            origen = vals.get('origen', self.origen.id)
            destino = vals.get('destino', self.destino.id)
            if ruta.direccion_origen_id.id != origen or ruta.direccion_destino_id.id != destino:
                raise UserError("El origen y destino de la ruta deben ser iguales al del viaje.")
        return super(Viajes, self).write(vals)
    
    # solo debe mostrar contactos hijos del solicitante
    @api.onchange('solicitante_id')
    def _onchange_solicitante_id(self):
        if self.solicitante_id:
            return {'domain': {'origen': [('id', 'child_of', self.solicitante_id.id)]}}
        return {'domain': {'origen': []}}

    # silo_id debe llenarse con el campo destino del albarán
    @api.onchange('silo_id')
    def _onchange_silo_id(self):
        if self.albaran_id and self.silo_id:
            # Actualizar la ubicación destino del albarán con la del silo seleccionado
            self.albaran_id.write({'location_dest_id': self.silo_id.id})
            _logger.info(f"Ubicación destino del albarán {self.albaran_id.name} actualizada a {self.silo_id.name}")


    @api.model
    def create_post_create_actions01(self, vals):
        # Crear el viaje como normalmente
        viaje = super(Viajes, self).create(vals)

        # Si hay un albarán asociado en la agenda, asignar su destino al silo del viaje
        if viaje.agenda and viaje.agenda.picking_id and viaje.agenda.picking_id.location_dest_id:
            viaje.silo_id = viaje.agenda.picking_id.location_dest_id.id

        return viaje


    # Impedir cambiar estados anteriores cuando hay un albarán asociado

    def action_borrador(self):
        if self.albaran_id:
            raise UserError('No se puede regresar al estado anterior porque hay un albarán asociado.')
        self.write({'state': 'coordinado'})



    
    @api.onchange('ruta_id')
    def _onchange_ruta_id(self):
        if self.ruta_id:
            # Lógica para determinar y asignar el gasto del viaje
            self.determinar_y_asignar_gasto_viaje()
    
    def determinar_y_asignar_gasto_viaje(self):
         # Verificar primero si el viaje fue creado desde un albarán
        if self.creado_desde_albaran:
           
            return
        
        # no se creen registros duplicados
        if not self.gastos_ids.filtered(lambda g: g.producto_id.id == self._get_gasto_viaje_producto_id()):
            # Obtener los productos de gasto de los ajustes
            config_params = self.env['ir.config_parameter'].sudo()
            gasto_con_impuesto_id = int(config_params.get_param('gms.gasto_viaje_con_impuesto_id'))
            gasto_sin_impuesto_id = int(config_params.get_param('gms.gasto_viaje_sin_impuesto_id'))
    
            # Determinar si el destino es de tipo 'puerto'
            es_destino_puerto = self.destino.tipo == 'puerto'
    
            # Seleccionar el producto de gasto adecuado
            producto_gasto_id = gasto_sin_impuesto_id if es_destino_puerto else gasto_con_impuesto_id
    
            # Obtener el producto de gasto
            producto = self.env['product.product'].browse(producto_gasto_id)
    
            # Obtener el precio unitario del producto
            precio_unitario = producto.standard_price
    
            # Calcular el precio total multiplicando por los kilómetros de la ruta
            precio_total_flete = self.peso_neto * self.kilometros_flete * precio_unitario
            
            # Obtener la moneda de compra del proveedor
            moneda_proveedor_id = self.transportista_id.property_purchase_currency_id.id if self.transportista_id else False
    
            # Crear nuevo registro de gasto de viaje
            self.env['gms.gasto_viaje'].create({
                'name': 'Flete',
                'producto_id': producto_gasto_id,
                'viaje_id': self.id,
                'precio_total': precio_total_flete,
                'proveedor_id': self.transportista_id.id,
                'moneda_id': moneda_proveedor_id,
                'estado_compra': 'no_comprado'
            })

    
    def _get_gasto_viaje_producto_id(self):
        # Este método auxiliar devuelve el ID del producto de gasto de viaje correspondiente
        config_params = self.env['ir.config_parameter'].sudo()
        gasto_con_impuesto_id = int(config_params.get_param('gms.gasto_viaje_con_impuesto_id'))
        gasto_sin_impuesto_id = int(config_params.get_param('gms.gasto_viaje_sin_impuesto_id'))
    
        # Determinar si el destino es de tipo 'puerto'
        es_destino_puerto = self.destino.tipo == 'puerto'
    
        # Seleccionar el producto de gasto adecuado
        return gasto_sin_impuesto_id if es_destino_puerto else gasto_con_impuesto_id




    @api.model
    def create(self, vals):
        # Generar el nombre del viaje si es necesario
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gms.viaje')
    
        # Si 'ruta_id' está presente en 'vals', actualizar 'kilometros_flete' según la ruta
        if 'ruta_id' in vals:
            ruta = self.env['gms.rutas'].browse(vals['ruta_id'])
            vals['kilometros_flete'] = ruta.kilometros
        else:
            # En caso de que no haya ruta, se podría establecer un valor por defecto o dejarlo en blanco.
            vals['kilometros_flete'] = 0.0
    
        # Crear el viaje
        record = super().create(vals)
    
        # Registrar un mensaje si el viaje fue creado desde una agenda
        if record.agenda:
            record.message_post(body="Este viaje fue creado desde una agenda.", subtype_xmlid="mail.mt_note")
    
        # Asignar la ruta y los gastos del viaje
        self._asignar_ruta_y_gastos(record, vals)
    
        return record


    def _asignar_ruta_y_gastos(self, record, vals):
        # Buscar una ruta que coincida con el origen y destino del viaje
        ruta = self.env['gms.rutas'].search([
            ('direccion_origen_id', '=', vals.get('origen')),
            ('direccion_destino_id', '=', vals.get('destino'))
        ], limit=1)

        # Si se encuentra una ruta, asignarla al viaje
        if ruta:
            record.ruta_id = ruta.id

        # Asignar los gastos de viaje
        record.determinar_y_asignar_gasto_viaje()




    def write(self, vals):
        # Actualiza el viaje como siempre
        result = super(Viajes, self).write(vals)

        # Asigna los gastos de viaje si se actualizó la ruta
        if 'ruta_id' in vals:
            for viaje in self:
                viaje.determinar_y_asignar_gasto_viaje()

        return result


    # actualizar al chofer
    @api.onchange('camion_id')
    def _onchange_camion_id(self):
        if self.camion_id:
            self.conductor_id = self.camion_id.conductor_id.id
        else:
            self.conductor_id = False




    def leer_peso_balanza_archivo(self):
        balanza = self.balanza_id
        if not balanza:
            raise UserError("Selecciona una balanza primero.")
    
       
        archivo_datos = '/Users/balanza/datos_balanza.txt'
    
        try:
            # Conectar vía SSH al servidor
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(balanza.direccion_servidor, username=balanza.usuario, password=balanza.contrasena)
    
            # Comando para obtener la última línea del archivo de datos
            comando_ssh = f"tail -n 1 {archivo_datos}"
            stdin, stdout, stderr = ssh.exec_command(comando_ssh)
            ultima_linea = stdout.read().decode().strip()
    
            ssh.close()
    
            if ultima_linea:
                peso = float(ultima_linea.split(' - Peso: ')[1])
                return peso
            else:
                raise UserError("No se recibieron datos de la balanza.")
        except Exception as e:
            _logger.error(f"Error al leer los datos de la balanza: {e}")
            raise UserError(f"No se pudo leer el peso de la balanza: {e}")
    
    def accion_leer_balanza(self):
        self.ensure_one()
        try:
            peso = self.leer_peso_balanza_archivo()
            self.write({'peso_bruto': peso})
        except Exception as e:
            _logger.error("Error al leer datos de la balanza: %s", e)
            raise UserError(f"No se pudo leer la balanza: {e}")



    def accion_calcular_tara(self):
       
        raise UserError(_('Esta es una acción de prueba para calcular la tara.'))



    def action_set_to_proceso(self):
        self.ensure_one()
        if self.state == 'terminado' and self.albaran_id and self.albaran_id.state != 'done':
            self.state = 'proceso'
        else:
            raise UserError("El viaje no puede pasar a estado 'Proceso' bajo las condiciones actuales.")



    def enviar_sms_solicitante(self):
        try:
            # Preparar el mensaje con detalles del viaje y las propiedades con sus mermas
            mensaje_sms = "Detalles del viaje: {}\n".format(self.name)
            for medida in self.medidas_propiedades_ids:
                mensaje_sms += "{}: {}\n".format(medida.propiedad.cod, medida.merma_kg)

            # Obtener el número de teléfono del solicitante
            telefono_solicitante = self.solicitante_id.mobile or self.solicitante_id.phone
            if telefono_solicitante:
                _logger.info("Enviando SMS al solicitante: %s", telefono_solicitante)
                self.env['sms.sms'].create({
                    'number': telefono_solicitante,
                    'body': mensaje_sms
                }).send()
                self.message_post(body=f"SMS enviado al solicitante ({telefono_solicitante}): {mensaje_sms}")
            else:
                raise UserError("El solicitante no tiene un número de teléfono registrado.")
        
        except Exception as e:
            error_message = f"Error al enviar SMS: {e}"
            _logger.error(error_message)
            self.message_post(body=error_message, message_type='comment', subtype_xmlid='mail.mt_comment')





    @api.onchange('peso_neto')
    def _onchange_peso_neto(self):
        if self.peso_neto:
            # Actualizar el precio total del flete en los gastos del viaje
            for gasto in self.gastos_ids:
                if gasto.name == 'Flete':  # Asegúrate de que este sea el nombre correcto del gasto de flete
                    # Calcular el nuevo precio total del flete
                    precio_unitario = gasto.producto_id.standard_price
                    gasto.precio_total = self.peso_neto * self.kilometros_flete * precio_unitario

    
    def action_liquidar_viajes(self):
        for viaje in self:
            # Asegúrate de que el viaje está en un estado terminado
            if viaje.state in ['terminado']:
                viaje.state = 'liquidado'
                
            else:
                raise UserError('No se puede liquidar uno o más de los viajes seleccionados.')
    

    def action_view_factura(self):
        self.ensure_one() 
        if self.factura_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': self.factura_id.id,
                'target': 'current',
            }
        else:
            raise UserError('No hay una factura asociada a este viaje.')



    


    @api.model
    def create(self, vals):
        # Verificar si 'peso_bruto', 'peso_neto' o 'tara' son negativos
        for field in ['peso_bruto', 'peso_neto', 'tara']:
            if field in vals and vals[field] < 0:
                raise UserError(_("%s no puede ser negativo." % field))
        return super(Viajes, self).create(vals)

    def write(self, vals):
        # Verificar si 'peso_bruto', 'peso_neto' o 'tara' son negativos
        for field in ['peso_bruto', 'peso_neto', 'tara']:
            if field in vals and vals[field] < 0:
                raise UserError(_("%s no puede ser negativo." % field))
        return super(Viajes, self).write(vals)