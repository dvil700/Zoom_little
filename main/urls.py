from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='main'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('photo', views.photo, name='photo'),
    path('feedback', views.FeedBackView.as_view(), name='feedback'),
    path('promo', views.PromoView.as_view(), name='promo'),

]