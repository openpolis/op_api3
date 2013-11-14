from django.contrib import admin
from popolo.models import Person, Organization, Membership, Post, ContactDetail, Identifier


class PersonAdmin(admin.ModelAdmin):
    pass

admin.site.register(Person)
admin.site.register(Organization)
admin.site.register(Membership)
admin.site.register(Post)
admin.site.register(ContactDetail)
admin.site.register(Identifier)