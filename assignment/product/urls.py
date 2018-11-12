from django.conf.urls import url
from product import views

urlpatterns = [
    url(r'^products/(?P<pk>[\w\-]+)/', views.ApproveInventory.as_view(),
        name='update-inventory'),
    url(r'^products/', views.InventoryView.as_view(),
        name='add-retrieve-inventory'),
]
