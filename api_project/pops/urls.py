from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import PersonViewSet, OrganizationViewSet, MembershipViewSet, PostViewSet, AreaViewSet
from .routers import DefaultPopsRouter

# Routers provide an easy way of automatically determining the URL conf
router = DefaultPopsRouter()

router.register(r'persons', PersonViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'memberships', MembershipViewSet)
router.register(r'posts', PostViewSet)
router.register(r'areas', AreaViewSet)


urlpatterns = patterns('',
    # django-rest-frameworks urls
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)

