from django.conf.urls import url
from . import views

# eg:url(r'^book/$',views.BookView.as_view()),
urlpatterns = [
    url(r'^settlement/$',views.CartListView.as_view()),
    url('^$', views.OrderCreateView.as_view()),
]
