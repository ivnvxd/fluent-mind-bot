from django.urls import include
from django.contrib import admin
from django.urls import path

from .views import IndexView


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    # path('login/', UserLoginView.as_view(), name='login'),
    # path('logout/', UserLogoutView.as_view(), name='logout'),

    path('bot/', include('bot.urls')),
    path('users/', include('users.urls')),
    path('chats/', include('chats.urls')),

    path('admin/', admin.site.urls),
]
