"""timetracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from timetracker.apps.users.urls import auth_patterns
from .schema import schema_view

urlpatterns = [
    path(
        "",
        include(arg=(auth_patterns, "auth_patterns"), namespace="auth"),
    ),
    path("users/", include("timetracker.apps.users.urls", namespace="users")),
    path("teams/", include(arg=("timetracker.apps.teams.urls", "teams"), namespace="teams")),
    path("projects/", include(arg=("timetracker.apps.projects.urls", "projects"), namespace="projects")),
    path("admin/", admin.site.urls),
    path("docs/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)