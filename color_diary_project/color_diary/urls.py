from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from . import views


router = routers.DefaultRouter()
router.register(r'colors', views.ColorViewSet, basename='color')
router.register(r'diaries', views.DiaryViewSet, basename='diary')
router.register(r'users', views.UserViewSet)


app_name = 'color_diary'
urlpatterns = [
    path('', views.top, name='top'),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register/done/', views.RegisterDoneView.as_view(), name='register-done'),
    path('register/<token>/', views.RegisterCompleteView.as_view(), name='register-complete'),
    path('diaries/', views.DiaryIndexView.as_view(), name='diary-index'),
    path('diaries/<str:diary_hash_id>/choose-color/', views.ChooseColorView.as_view(), name='choose-color'),
    path('diaries/<str:diary_hash_id>/', views.EditDiaryView.as_view(), name='edit-diary'),
    path('diaries/<str:diary_hash_id>/delete/', views.DeleteDiaryView.as_view(), name='delete-diary'),
    path('colors/', views.ColorIndexView.as_view(), name='color-index'),
    path('colors/<str:color_hash_id>/', views.EditColorView.as_view(), name='edit-color'),
    path('colors/<str:color_hash_id>/delete/', views.DeleteColorView.as_view(), name='delete-color'),
]
