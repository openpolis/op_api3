from django.contrib import admin
from popolo.models import Person, Organization, Membership, Post


class PersonAdmin(admin.ModelAdmin):
    pass

admin.site.register(Person)
admin.site.register(Organization)
admin.site.register(Membership)
admin.site.register(Post)