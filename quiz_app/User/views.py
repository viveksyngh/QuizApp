from django.shortcuts import render
from quiz_app.utils import(validate_params,
                                    gen_password_hash,
                                    send_400,
                                    send_200,
                                    send_404)
import uuid
from quiz_app.redis_utils import (create_token,
                                  get_token)
from django.views.generic import View
from models import User

# Create your views here.


class Register(View):
    """Register a user."""

    def __init__(self):
        
        self.response = {
            'message': '',
            'result': {}
            }

    def dispatch(self, request, *args, **kwargs):
        return super(Register, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        req_data = request.POST
        reqd_params = ['first_name', 'last_name', 'email_id', 
                      'mobile_no', 'password']
        
        is_valid, res_str = validate_params(req_data, reqd_params)
        if not is_valid:
            self.response["message"] = res_str
            return send_400(self.response)

        try:
            user = User.objects.get(email_id=req_data.get('email_id'))
        except User.DoesNotExist:
            user = User(
                user_id=uuid.uuid1(),
                first_name=req_data.get('first_name'),
                last_name=req_data.get('last_name'),
                middle_name=req_data.get('middle_name'),
                email_id=req_data.get('email_id'),
                mobile_no=req_data.get('mobile_no'),
                password=gen_password_hash(req_data.get('password'))
                )
            user.save()
            self.response["message"] = 'Registered successfully.'
            self.response["result"]["user_id"] = user.user_id
        else:
            self.response["message"] = "Email already registered.Try to login."
            return send_400(self.response)
        return send_200(self.response)


class Login(View):
    """View to login."""

    def __init__(self):

        self.response = {
            'message': '',
            'result': {}
        }

    def dispatch(self, request, *args, **kwargs):
        return super(Login, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        req_data = request.POST
        reqd_params = ['email_id', 'password']
        is_valid, res_str = validate_params(req_data, reqd_params)
        
        if not is_valid:
            self.response["message"] = res_str
            return send_400(self.response)

        try:
            # Check if email id is registered or not.
            user = User.objects.get(email_id=req_data.get('email_id'))
        except User.DoesNotExist:
            self.response["message"] = "Email id is not registered. Please register."
            return send_404(self.response)
        else:
            # Match the hashed value of stored password and enterd password.
            if user.password != gen_password_hash(req_data.get("password")):
                self.response["message"] = "Password is incorrect."
                return send_400(self.response)

            # Creating a token in redis to initaite the session
            create_token(user.user_id, uuid.uuid1(), 900)
            self.response["message"] = "Logged in successfully."
            # Sending cid and token for future communication
            self.response["result"]["cid"] = user.user_id
            self.response["result"]["token"] = get_token(user.user_id)
        return send_200(self.response)
