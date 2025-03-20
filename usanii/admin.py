from django.contrib import admin

# Register your models here.

#from . models import Homepage

from . models import Aboutpage, Artists, Homepage, Artworks, Exhibitions, Contact, Footer, Customer

admin.site.register(Aboutpage)

admin.site.register(Artists)

admin.site.register(Homepage)

admin.site.register(Artworks)

admin.site.register(Exhibitions)

admin.site.register(Contact)

admin.site.register(Footer)

admin.site.register(Customer)