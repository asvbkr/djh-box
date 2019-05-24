from django.urls import path, include

from django.contrib import admin

admin.autodiscover()

import djh_app.views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", djh_app.views.index, name="index"),
    path("db/", djh_app.views.db, name="db"),
    path("admin/", admin.site.urls),
]
