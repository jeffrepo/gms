# -*- coding: utf-8 -*-
{
    'name': 'GMS',
    'summary': 'Módulo de Barraca Artigas Silveira',
    'description': 'Módulo para Barraca Artigas Silveira',
    'author': '',
    'website': '',
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','product','sale','purchase','stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/gms_agenda.xml',

    ],
    'images': [
        'static/description/icon.png',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}

