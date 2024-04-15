# -*- coding: utf-8 -*-
{
    'name': 'GMS',
    'summary': 'Módulo de Barraca Artigas Silveira',
    'description': 'Módulo para Barraca Artigas Silveira',
    'author': '',
    'website': '',
    'icon': '/gms/static/description/Balanza.png',
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','product','sale','purchase','stock', 'account'],
    'data': [
        'views/views.xml',
        'views/gms_viajes.xml',
        'views/gms_agenda.xml',
        'security/ir.model.access.csv',
        'report/report_gms_viajes.xml',
        'views/report.xml',

    ],
    'images': [
        'static/description/icon.png',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}

