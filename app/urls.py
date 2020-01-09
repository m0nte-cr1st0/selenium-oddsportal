from django.urls import path, re_path

from . import views


urlpatterns = [
    path('signup/', views.UserCreateView.as_view(), name='signup'),
    path('', views.run),
    path('2', views.run2),
    path('account/<int:pk>/', views.ProfileView.as_view(), name="profile_detail"),
    path('account/<int:pk>/edit/', views.ProfileEditView.as_view(), name="profile_update"),
    path('predictions/', views.NextPredictionsListView.as_view(), name="predictions_next"),
    path('predictions_last/', views.LastPredictionsListView.as_view(), name="predictions_last"),
    path('prediction_create/', views.PredictionCreateView.as_view(), name="prediction_create"),
    path('capper_rating/', views.CapperListView.as_view(), name="capper_rating")
]
