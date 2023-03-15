from django.urls import include
from django.contrib import admin
from django.urls import path

from .views import IndexView


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    # path('login/', UserLoginView.as_view(), name='login'),
    # path('logout/', UserLogoutView.as_view(), name='logout'),

    path('bot/', include('fluent_mind.bot.urls')),
    path('users/', include('fluent_mind.users.urls')),

    path('admin/', admin.site.urls),
]
