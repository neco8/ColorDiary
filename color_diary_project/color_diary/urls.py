from django.urls import path

from . import views

app_name = 'color_diary'
urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('diaries/', views.DiaryIndexView.as_view(), name='diary-index'),
    path('diaries/<str:diary_hash_id>/choose-color/', views.ChooseColorView.as_view(), name='choose-color'),
    path('diaries/<str:diary_hash_id>/', views.EditDiaryView.as_view(), name='edit-diary'),
    path('diaries/<str:diary_hash_id>/delete/', views.DeleteDiaryView.as_view(), name='delete-diary'),
    path('colors/', views.ColorIndexView.as_view(), name='color-index'),
    path('colors/<str:color_hash_id>/', views.EditColorView.as_view(), name='edit-color'),
    path('colors/<str:color_hash_id>/delete/', views.DeleteColorView.as_view(), name='delete-color'),
]
