from django.conf.urls import url
from . import views

# eg:url(r'^book/$',views.BookView.as_view()),
urlpatterns = [
    url('^cart/$', views.CartView.as_view()),
    url('^cart/selection/$', views.CartSelectView.as_view()),

]
