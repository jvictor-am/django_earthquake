from django.contrib import admin
from django.urls import path
from .models import City, CityLog, SearchResult
from .views import search_earthquakes


class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)
    exclude = ('latitude', 'longitude')
        
    def has_change_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('earthquakes/search/', self.admin_site.admin_view(search_earthquakes), name='search_earthquakes'),
        ]

        return custom_urls + urls


@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ('earthquake_magnitude', 'earthquake_location', 'earthquake_date', 'city', 'search_start_date', 'search_end_date', 'nearest_distance')
    list_filter = ('earthquake_date', 'city')
    search_fields = ('earthquake_location',)

    def has_add_permission(self, request):
        return False
    
    def get_readonly_fields(self, request, obj=None):
        return ('earthquake_magnitude', 'earthquake_location', 'earthquake_date', 'city', 'search_start_date', 'search_end_date', 'nearest_distance')
    
    def has_change_permission(self, request, obj=None):
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "city":
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(City, CityAdmin)
admin.site.register(CityLog)