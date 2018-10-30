from django.conf.urls import url
from . import views
from rest_framework.routers import DefaultRouter

# eg:url(r'^book/$',views.BookView.as_view()),
urlpatterns = [
    # url(r'^areas/$',views.AreaListView.as_view()),
    # url(r'^areas/(?P<pk>\d+)/$',views.AreaRetrieveView.as_view()),
]

route = DefaultRouter()
route.register('areas',views.AreaViewSet,base_name='areas')
urlpatterns += route.urls