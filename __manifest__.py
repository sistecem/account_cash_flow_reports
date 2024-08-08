# -*- coding: utf-8 -*-
#############################################################################
# SISTECEM
#############################################################################

{
    'name': 'Advanced Cash Flow Reports',
    'version': '14.0.1.0.1',
    'summary': """Generate cash flow reports in PDF and Excel""",
    'description': """Generate cash flow statement reports in PDF and Excel""",
    'author': "Sistecem",
    'company': 'Sistecem',
    'maintainer': 'Sistecem',
    'website': "https://www.sistecem.com",
    'category': 'Accounting',
    'depends': ['base', 'account','hr'],
    'data': ['security/ir.model.access.csv',
             'wizard/account_wizard.xml',
             'views/action_manager.xml',
             'report/print_report.xml',
             'report/pdf_template.xml',
             ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
