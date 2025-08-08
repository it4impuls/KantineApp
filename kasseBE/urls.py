from rest_framework import routers
from django.urls import include, path
from .views import UserViewSet, OrderViewSet, OrderBillViewSet


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'bills', OrderBillViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    # path('api/', include('rest_framework.urls', namespace='rest_framework'))
]
