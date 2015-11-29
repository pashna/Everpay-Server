from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^login/$', 'eAPI.views.login', name='login'),
                       url(r'^logout/$', 'eAPI.views.logout', name='logout'),

                       url(r'^users/add/$', 'eAPI.views.add_users', name='add_users'),

                       url(r'^groups/$', 'eAPI.views.get_groups', name='get_groups'),
                       url(r'^groups/add/$', 'eAPI.views.add_groups', name='add_groups'),
                       url(r'^groups/edit/$', 'eAPI.views.edit_groups', name='edit_groups'),

                       url(r'^groups/members/$', 'eAPI.views.get_members', name='get_members'),
                       url(r'^groups/members/add/$', 'eAPI.views.add_members', name='add_members'),
                       url(r'^groups/members/remove/$', 'eAPI.views.remove_members', name='add_members'),
                       url(r'^groups/history/$', 'eAPI.views.get_groups_history', name='get_groups_history'),

                       url(r'^bills/add/$', 'eAPI.views.add_bills', name='add_bills'),
                       url(r'^bills/edit/$', 'eAPI.views.edit_bills', name='edit_bills'),
                       url(r'^bills/details/$', 'eAPI.views.get_bills_details', name='get_bills_details'),
                       url(r'^bills/remove/$', 'eAPI.views.remove_bills', name='remove_bills'),
                       url(r'^bills/restore/$', 'eAPI.views.restore_bills', name='restore_bills'),

                       url(r'^debts/$', 'eAPI.views.get_user_debts', name='get_debts'),
                       url(r'^debts/add/$', 'eAPI.views.add_debts', name='add_debts'),
                       url(r'^debts/edit/$', 'eAPI.views.edit_debts', name='edit_debts'),
                       url(r'^debts/details/$', 'eAPI.views.get_debts_details', name='get_debts_details'),
                       url(r'^debts/remind/$', 'eAPI.views.remind_about_debts', name='remind_about_debts'),

                       url(r'^gcm/register/$', 'eAPI.views.register_devices', name='register_devices'),
                       url(r'^gcm/unregister/$', 'eAPI.views.unregister_devices', name='unregister_devices'),

                       url(r'', include('gcm.urls')),

                       url(r'', 'eAPI.views.page_not_found', name='404'))
