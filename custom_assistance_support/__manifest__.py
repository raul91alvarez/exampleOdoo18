# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Custom Assistance Support',
    'version': '1.0.6',
    'depends': ['helpdesk', 'mail'],
    'author': 'Synapsis',
    'website': 'https://synapsisbpo.com/',
    'category': 'Helpdesk',
    'description': 'Notifies in the General channel when a ticket is created',
    'installable': True,
    'auto_install': False,
    'data': [
        'data/ticket_type_data.xml',
        'views/ticket_type_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/follower_group_views.xml',
        'security/ir.model.access.csv',
    ],
    'migrations': [
        'migrations/1.0.0/',
    ],
}
