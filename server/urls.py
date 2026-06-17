
from django.contrib import admin
from django.urls import path,  include
from django.conf.urls.static import static, settings


urlpatterns = [

    path("api/", include('store.urls')),
    path('admin/', admin.site.urls),
    path('', include('payments.urls')), # new

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)