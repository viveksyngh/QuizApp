from django.shortcuts import render
from django.views.generic import View
from quiz_app.utils import(login, send_400, send_404, send_200,
                           create_index_in_elastic_search, INDEX_NAME,
                           DOC_TYPE, search_in_elastic)
import json
from quiz_app.settings import API_HOME
from models import (Question, Option, Vote)
from django.db.models import Count


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

        question = Question.objects.create(question_text=question_text,
                                          user_id=cid)
        ques_url = API_HOME + 'quiz/v1/questions/' + str(question.pk) + '/'
        question.question_url = ques_url
        question.save()

        create_list = []
        for option in option_list:
            opt = Option(option_text=option,
                         question=question)
            create_list.append(opt)
        Option.objects.bulk_create(create_list)

        self.response["message"] = "Question created successfully."
        self.response["result"]["url"] = ques_url
        self.response["result"]["question_id"] = question.question_id
        create_index_in_elastic_search(question.serializer(), question.question_id)
        return send_200(self.response)


    @login
    def get(self, request, *args, **kwargs):
        cid = request.GET.get('cid')
        options = Option.objects.select_related('question').filter(question__user_id=cid)
        votes = Vote.objects.values('option_id').annotate(vote_count=Count('vote_id'))
        vote_count_map = {}
        for vote in votes:
             vote_count_map[vote['option_id']] = vote['vote_count']
        questions = {}
        for option in options:
            key = option.question_id
            if key not in questions:
                item = {
                    'question_text': option.question.question_text,
                    'question_id': key,
                    'options': []
                }
                questions[key] = item
            opt = option.serializer()
            opt["vote_count"] = vote_count_map.get(opt["id"], 0)
            questions[key]["options"].append(opt)
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
            question = Question.objects.get(question_id=kwargs.get('question_id'))
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
        return super(VoteView, self).dispatch(request, *args, **kwargs)

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
            self.response["message"] = "You have already voted for this question."
            return send_400(self.response)
        return send_200(self.response)

    @login
    def get(self, request, *args, **kwargs):
        req_data = request.GET
        cid = req_data.get('cid')
        votes = Vote.objects.select_related().filter(option__question__user_id=cid).order_by('-option_id')
        vote_list = []
        for vote in votes:
            value = {}
            value["question_text"] = vote.option.question.question_text
            value["option"] = vote.option.option_text
            value["voted_by"] = vote.user.first_name + ' ' + vote.user.middle_name + ' ' + vote.user.last_name
            vote_list.append(value)
        self.response["message"] = "Data received successfully."
        self.response["result"]["votes"] = vote_list
        return send_200(self.response)


class SearchQuestions(View):
    
    def __init__(self):
        """Initializes the view object and response variable."""
        self.response = {
            'message': '',
            'result': {}
        }

    def dispatch(self, request, *args, **kwargs):
        """Relay the request to corresponding method if it is defined"""
        return super(SearchQuestions, self).dispatch(request, *args, **kwargs)

    @login
    def get(self, request):
        search_text = request.GET["search_text"]
        results = search_in_elastic(search_text)
        question_list = []
        for res in results:
            # ques = {}
            # ques["question_text"] = res.question
            # ques["options"] = []
            # for option in res.options:
            #     opt = {}
            #     opt["id"] = option.id
            #     opt["option"] = option.option
            #     ques["options"].append(opt)
            # ques["id"] = res.id
            question_list.append(res.to_dict())
        self.response["message"] = "Data received successfully."
        self.response["result"]["question_list"] = question_list
        return send_200(self.response)
