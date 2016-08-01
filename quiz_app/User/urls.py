from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import url
from views import(Register,
                  Login)

urlpatterns = [
                url(r'^v1/register/$',
                    csrf_exempt(Register.as_view())),
                url(r'^v1/login/$',
                    csrf_exempt(Login.as_view())),        
        ]