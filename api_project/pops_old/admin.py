from django.contrib import admin
from django.forms import Textarea

from pops.models import *


class ProfessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'main')


class ProfessionInline(admin.TabularInline):
    model = PersonHasProfessionw
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':60})},
    }
    raw_id_fields = ('profession',)
    extra = 0


class EducationLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'main')

class EducationInline(admin.TabularInline):
    model = PersonHasEducationLevel
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':60})},
    }
    raw_id_fields = ('education_level',)
    extra = 0


class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'birth_location', 'op_id')
    raw_id_fields = ('birth_location',)
    inlines = (ProfessionInline, EducationInline,)
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', ('birth_date', 'death_date'), 'birth_location', 'sex')
        }),
    )

admin.site.register(Person, PersonAdmin)
admin.site.register(Profession, ProfessionAdmin)
admin.site.register(EducationLevel, EducationLevelAdmin)