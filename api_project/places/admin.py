from django.contrib import admin
from django.contrib.gis import forms
from django.contrib.gis.db import models
from treeadmin.admin import TreeAdmin
from places.models import Place, PlaceType, Identifier, PlaceLink, \
    PlaceGEOInfo, ClassificationTreeNode, ClassificationTreeTag, Language, PlaceAcronym, PlaceI18Name, PlaceIdentifier


class PlaceGEOInfoInlineAdmin(admin.StackedInline):
    model = PlaceGEOInfo
    extra = 0
    formfield_overrides = {
        models.MultiPolygonField: {
            'widget': forms.OSMWidget(
                attrs={'map_width': 600, 'map_height': 400}
            )
        },
    }
class PlaceIdentifierInline(admin.TabularInline):
    model = PlaceIdentifier
    extra = 0

class AcronymInlineAdmin(admin.StackedInline):
    model = PlaceAcronym
    extra = 0

class PlaceI18NameInlineAdmin(admin.TabularInline):
    search_fields = ('name', 'language__iso639_1_code')
    model = PlaceI18Name
    extra = 0
    list_display = ('name', 'language')

class PlaceAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)
    raw_id_fields = ('new_places',)
    list_filter = ('place_type',)
    inlines = [
        PlaceIdentifierInline,
        AcronymInlineAdmin,
        PlaceI18NameInlineAdmin,
        PlaceGEOInfoInlineAdmin,
    ]



class IdentifierAdmin(admin.ModelAdmin):
    list_display = ('scheme', 'name', 'slug')


class LanguageAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'iso639_1_code')




class ClassificationTreeNodeAdmin(TreeAdmin):
    mptt_level_indent = 10
    mptt_indent_field = "id"
    list_display = ('id', 'place', 'tag', 'equivalent_to',)
    raw_id_fields = ('parent', 'place', 'equivalent_to',)
    search_fields = ('place__name',)
    list_filter = ('tag',)


admin.site.register(Language, LanguageAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(PlaceType)
admin.site.register(Identifier, IdentifierAdmin)
admin.site.register(ClassificationTreeNode, ClassificationTreeNodeAdmin)
admin.site.register(ClassificationTreeTag)