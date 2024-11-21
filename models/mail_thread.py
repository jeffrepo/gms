# models/mail_thread.py
from odoo import models, _

class CustomMailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _mail_track_order_fields(self, tracked_fields):
        #modificación en la clave de ordenación.
        fields_track_info = []
        for name, field in tracked_fields.items():
            track_value = getattr(self, name)
            fields_track_info.append((name, track_value))
        
        # Modificación para manejar tipos mixtos
        fields_track_info.sort(key=lambda item: (str(item[1]), str(item[0])), reverse=True)
        
        return fields_track_info
