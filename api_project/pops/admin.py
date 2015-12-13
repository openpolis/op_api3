from popolo.models import Area, Person, Organization, Membership, Post, ContactDetail, Identifier
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline


class OtherIdentifierInline(GenericTabularInline):
    model = Identifier
    extra = 0

class AreaAdmin(admin.ModelAdmin):
    inlines = [
        OtherIdentifierInline,
    ]

class PersonAdmin(admin.ModelAdmin):
    pass

admin.site.register(Area, AreaAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Organization)
admin.site.register(Membership)
admin.site.register(Post)
admin.site.register(ContactDetail)
admin.site.register(Identifier)