from .forms import ReCaptcha
from django.http import HttpResponseForbidden
import requests
from rest_framework import serializers
import json
from decimal import Decimal
from Zoom_little import settings
from abc import ABC, abstractmethod
from Zoom_little import settings


class CaptcaDataSourceAbstract(ABC):
    @abstractmethod
    def get_data(self) -> str:
        pass


class GoogleDataSource(CaptcaDataSourceAbstract):
    def __init__(self, secret, recapcha_field):
        self._secret = secret
        self._recaptcha_field = recapcha_field
    def get_data(self) -> str:
        google_request = requests.post('https://www.google.com/recaptcha/api/siteverify',
                                       dict(secret=self._secret, response=self._recaptcha_field))
        return google_request.text


class CaptchaSerializerABC:
    @property
    @abstractmethod
    def is_valid(self):
        pass

    @abstractmethod
    def is_succeeded(self):
        pass

    @abstractmethod
    def get_score(self):
        pass

    @abstractmethod
    def get_action(self):
        pass


class ReCaptchaSerializer(serializers.Serializer, CaptchaSerializerABC):
    success = serializers.BooleanField(required=True)
    score = serializers.DecimalField(max_digits=None, required=False, decimal_places=1)
    action = serializers.CharField(required=False)
    hostname = serializers.CharField(required=False)
    challenge_ts = serializers.CharField(required=False)
    error_codes = serializers.ListField(child=serializers.CharField(), required=False,
                                        allow_empty=True)

    def is_succeeded(self):
        return self.validated_data['success']

    def get_score(self):
        return self.validated_data['score']

    def get_action(self):
        return self.validated_data['action'].lower()


class ReCaptcha3:
    def __init__(self, captcha_data_source: CaptcaDataSourceAbstract, serializer_cls: type,
                 threshold_value=Decimal('0.5'), action_name=None):
        self._captcha_data_source = captcha_data_source
        self._serializer_class = serializer_cls
        self._action_name = action_name
        self._threshold = threshold_value

    def parse_json(self, data_str):
        return json.loads(data_str)

    def get_serializer(self, data):
        return self._serializer_class(data=data)

    def is_robot(self):
        str_data = self._captcha_data_source.get_data()
        data = self.parse_json(str_data)
        if 'error-codes' in data:
            data['error_codes'] = data.pop('error-codes')
        serializer = self.get_serializer(data)
        if not serializer.is_valid():
            return True

        if not serializer.is_succeeded():
            return True

        if not (self._action_name and self._action_name == serializer.get_action()):
            return True
         
        if serializer.get_score() < self._threshold:
            return True
        return False


recaptcha_site_key = settings.RECAPTCHA_SITE_KEY

def get_captcha_src():
    return '< script  src = "https://www.google.com/recaptcha/api.js?render={}" > < / script >'.format(settings.RECAPTCHA_SITE_KEY)

def re_captcha_dec(meth):
    def wrapper(self, request):
        form = ReCaptcha(request.POST)
        if not form.is_valid():
            return HttpResponseForbidden()
        secret = settings.RECAPTCHA_SECRET
        recaptcha_field = form.cleaned_data['captcha_token']

        data_source = GoogleDataSource(secret, recaptcha_field)
        recaptcha = ReCaptcha3(data_source, ReCaptchaSerializer, threshold_value=Decimal('0.5'), action_name='submit')
        if recaptcha.is_robot():
            return HttpResponseForbidden()
        return meth(self, request)
    return wrapper
