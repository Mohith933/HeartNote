from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("",views.home,name="home"),   path("dashboard/",views.dashboard,name="dashboard"),
    path("api/generate/", views.generate_text, name="generate_text"),
    path("api/dashboard/", views.generate_dashboard, name="generate_dashboard"),
    path("admin_stats/",views.admin_stats, name="admin_stats"),
    path("api/signup/", views.signup_api),
    path("api/login/",views.login_api),
    path("api/profile/", views.profile_api),
    path("api/logout/",views.logout_api),
    path("api/upload-avatar/", views.upload_avatar),
    path("api/avatar/", views.get_avatar),
    path("api/delete-account/",views.delete_account),
    path("api/save-writing/", views.save_writing),
    path("api/get-writings/", views.get_writings),
    path("api/delete-writing/", views.delete_writing),
    path("api/reset-app/", views.reset_app),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)












