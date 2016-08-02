from django.shortcuts import render
from django.views.generic import View
from quiz_app.utils import login, send_400, send_404
import json
from quiz_app.setting import API_HOME

# Create your views here.


class QuestionView(View):
    """View to create and retrieve all question of user."""

    def __init__(self):
        """Initializes the view object and response variable."""
        self.response = {
            'message': '',
            'result': {}
        }

    def dispatch(self, request, *args, **kwargs):
        """Relay the request to corresponding method if it is defined"""
        return super(QuestionView, self).dispatch(request, *args, **kwargs)

    @login
    def post(self, request, *args, **kwargs):
        req_data = request.POST
        question_text = req_data.get("question_text")
        options = req_data.get("options")
        cid = req_data.get('cid')

        if question_text is None or options is None:
            self.response["message"] = "Invalid request paramters."
            return send_400(self.response)
        
        try:
            option_list = json.loads(options)
        except ValueError:
            self.response["message"] = "Invalid options."
            return send_400(self.response)

        if len(question_text) == 0 or len(question_text) > 300:
            self.response["message"] = "Question text cannot be greater than 300 chars."
            return send_400(self.response)

        if len(option_list) > 0:
            for option in option_list:
                if len(option) == 0:
                    self.response["message"] = "Option text length must be greater that zero"
                    return send_400(self.response)

                if len(option) > 60:
                    self.response["message"] = "Option text cannot be greater that 60 chars."
                    return send_400(self.response)

        question = Question.object.create(question_text=question_text,
                                          user_id=cid)
        ques_url = API_HOME + 'quiz/v1/questions/' + str(question.pk) + '/'
        question.question_url = ques_url
        question.save()

        create_list = []
        for option in option_list:
            opt = Option(option_text=option_text,
                         question=question)
            create_list.append(opt)
        Option.objects.bulk_create(create_list)

        self.response["message"] = "Question created successfully."
        self.response["result"]["url"] = ques_url
        return send_200(self.response)


    @login
    def get(self, request, *args, **kwargs):
        cid = request.GET.get('cid')
        options = Option.objects.select_related('question').filter(question__user_id=cid)
        questions = {}
        for option in options:
            key = option.question_id
            if key not in questions:
                item = {
                    'question_text': option.question_text,
                    'question_id': key,
                    'options' = []
                }
                questions[key] = item
            questions[key]["options"].append(option.serializer())
        self.response["message"] = "Question details received successfully."
        self.response["result"]["questions"] = questions
        return send_200(self.response)


class QuestionDetailsView(View):
    """View to get a details of a question."""

    def __init__(self):
        """Initializes the view object and response variable."""
        self.response = {
            'message': '',
            'result': {}
        }

    def dispatch(self, request, *args, **kwargs):
        """Relay the request to corresponding method if it is defined"""
        return super(QuestionDetailsView, self).dispatch(request, *args, **kwargs)

    @login
    def get(self, request, *args, **kwargs):
        try:
            question = Question.objects.get(question_id=question_id)
        except Question.DoesNotExist:
            self.response["message"] = "Question does not exists."
            return send_404(self.response)
        else:
            self.response["result"]["question"] = question.serializer()
            self.response["message"] = "Question details received successfully."
        return send_200(self.response)


class VoteView(View):

    def __init__(self):
        """Initializes the view object and response variable."""
        self.response = {
            'message': '',
            'result': {}
        }

    def dispatch(self, request, *args, **kwargs):
        """Relay the request to corresponding method if it is defined"""
        return super(QuestionDetailsView, self).dispatch(request, *args, **kwargs)

    @login
    def post(self, request, *args, **kwargs):
        req_data = request.POST
        question_id = req_data.get("question_id")
        option_id = req_data.get("option_id")
        cid = req_data.get("cid")
        try:
            question = Question.objects.get(question_id=question_id)
            option = Option.objects.get(question=question, option_id=option_id)
            vote = Vote.objects.get(option__question=question, user_id=cid)
        
        except Question.DoesNotExist:
            self.response["message"] = "Question does not exists."
            return send_404(self.response)
        
        except Option.DoesNotExist:
            self.response["message"] = "Not a valid option for this question"
            return send_404(self.response)
        
        except Vote.DoesNotExist:
            vote = Vote.objects.create(option=option,
                        user_id=cid)
            self.response["message"] = "Your vote has been received successfully."
        else:
            self.message["message"] = "You have already voted for this question."
        return send_200(self.response)
