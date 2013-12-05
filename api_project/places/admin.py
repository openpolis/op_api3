from django.contrib import admin
from treeadmin.admin import TreeAdmin
from places.models import Place, PlaceType, Identifier, PlaceLink, \
    PlaceGEOInfo, ClassificationTreeNode, ClassificationTreeTag, Language, PlaceAcronym, PlaceI18Name, PlaceIdentifier


class PlaceIdentifierInline(admin.TabularInline):
    model = PlaceIdentifier
    extra = 0


class PlaceAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)
    raw_id_fields = ('new_places',)
    list_filter = ('place_type',)
    inlines = [
        PlaceIdentifierInline,
    ]


class AcronymAdmin(admin.ModelAdmin):
    search_fields = ('acronym',)
    list_display = ('acronym', 'place',)
    raw_id_fields = ('place',)


class LanguageAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'iso639_1_code')


class PlaceI18NameAdmin(admin.ModelAdmin):
    search_fields = ('name', 'language__iso639_1_code')
    list_display = ('name', 'language')


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
admin.site.register(Identifier)
admin.site.register(PlaceAcronym, AcronymAdmin)
admin.site.register(PlaceI18Name, PlaceI18NameAdmin)
admin.site.register(PlaceLink)
admin.site.register(PlaceGEOInfo)
admin.site.register(ClassificationTreeNode, ClassificationTreeNodeAdmin)
admin.site.register(ClassificationTreeTag)