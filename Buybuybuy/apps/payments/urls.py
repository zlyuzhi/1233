from django.conf.urls import url
from . import views

# eg:url(r'^book/$',views.BookView.as_view()),
urlpatterns = [
    url('^orders/(?P<order_id>\d+)/payment/$',views.AliPayURLView.as_view()),
]
