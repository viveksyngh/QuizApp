from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import url
from views import(QuestionView,
                  QuestionDetailsView,
                  VoteView)

urlpatterns = [
                url(r'^v1/questions/$',
                    csrf_exempt(QuestionView.as_view())),
                url(r'^v1/questions/(?P<question_id>[0-9]+)/$',
                    csrf_exempt(QuestionDetailsView.as_view())), 
                url(r'^v1/votes/$',
                    csrf_exempt(VoteView.as_view())), 

        ]