from django.urls import path
from .views import AllVoterBulkInsertAPI
from . import views

urlpatterns = [
    path("api/all-voters/import/", AllVoterBulkInsertAPI.as_view(), name="allvoter-import"),
    path('', views.voter_list, name='home'),\
          path('login/', views.custom_login, name='login'),
    path('api/voters/', views.get_voters, name='get_voters'),
    path('api/voters/create/', views.create_voter, name='create_voter'),
    path('api/voters/<int:voter_id>/update/', views.update_voter, name='update_voter'),
    path('api/voters/<int:voter_id>/delete/', views.delete_voter, name='delete_voter'),
    path('api/voters/<int:voter_id>/', views.get_voter_detail, name='get_voter_detail')
]
