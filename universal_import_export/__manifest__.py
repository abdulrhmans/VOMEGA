# -*- coding: utf-8 -*-

{'name': 'Universal Import/Export product data in Batch',
 'version': '11.2018.11.23.1',
 'category': 'other',
 'depends': ['sale_stock'],
 'author': "Terra Colligo",
 'license': 'AGPL-3',
 'website': 'www.terracolligo.com',
 'data': [
        'security/ir.model.access.csv',
        'views/product_import_batch_view.xml',
        'views/export.xml',
        ],
  "qweb": [
        'static/src/xml/*.xml',
        ],
 'installable': True,
 'application': True,
 }
