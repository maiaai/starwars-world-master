from django.urls import path
from app.views import CollectionsView, GetCollection, fetch

app_name = 'app'

urlpatterns = [
    path('collections/', CollectionsView.as_view(), name="collections"),
    path('collections/<int:pk>', GetCollection.as_view(), name="details"),
    path('collections/fetch/', fetch, name="fetch"),
]
