from django.conf.urls import url
from . import views

# eg:url(r'^book/$',views.BookView.as_view()),
urlpatterns = [
    url(r'^qq/authorization/$',views.QQurlView.as_view()),
    url(r'^qq/users/$',views.QQLoginView.as_view()),
    # url(r'^qq/users/$',views.QQUserView.as_view()),

]

