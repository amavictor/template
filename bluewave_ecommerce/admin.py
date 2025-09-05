from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

# This will be loaded when admin is accessed
def customize_admin():
    try:
        # Unregister default models that admin doesn't need
        admin.site.unregister(Group)
        admin.site.unregister(Site)
    except admin.sites.NotRegistered:
        pass  # Already unregistered

    # Customize admin site
    admin.site.site_header = 'TechMart Admin'
    admin.site.site_title = 'TechMart Admin Portal'
    admin.site.index_title = 'Welcome to TechMart Administration'

# Auto-run customization
customize_admin()