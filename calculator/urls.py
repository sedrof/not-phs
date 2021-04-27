from django.urls import path, include
from rest_framework import routers
from calculator .views import *
from . import views
from calculator . views import api_transaction

urlpatterns = [
    # path('transaction/<int:transaction_id>/', views.transaction_print, name='transaction_print'),
    path('pdf_view/<chp_reference>/', views.ViewPDF, name="pdf_view"),
    path('pdf/', views.pdfs, name="pdfss"),
    path('report/<chp>/', views.api_transaction, name='get_report'),
    path('post/', views.post_api, name='post_report'),
]