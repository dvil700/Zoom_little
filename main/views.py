from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from .forms import CallBackForm, PromoForm
from django.views import View
from .services import PromoSimpleService, PromoCodeGeneratorService, OnePromoOnePersonStrategy, PromoExistsError
from django.core.mail import send_mail
from datetime import datetime


# Create your views here.

def index(request):
    return render(request, 'main/index.html', {})


def about(request):
    return render(request, 'main/about.html', {'page_name': "О нас"})


def contact(request):
    return render(request, 'main/contact.html', {'page_name': "Контакты"})


def photo(request):
    return render(request, 'main/photo.html', {'page_name': "Фото на документы"})



class FormJsonResponseFactory:
    def __init__(self):
        self._fields_errors = []

    def _get_form_errors(self, form):
        for field in form:
            for error in field.errors:
                self._fields_errors.append(dict(id=field.id_for_label, error=error))

    def add_form(self, form):
        if form.is_valid():
            return
        self._get_form_errors(form)

    def get_response(self):
        result = True
        if len(self._fields_errors) > 0:
            result = False
        response_dict = dict(result=result, general_errors='', fields_errors=self._fields_errors)
        return JsonResponse(response_dict)

    def get_negative_response(self, errors: list, show_form_errors=True):
        response_dict = dict(result=False, general_errors=errors, fields_errors=[])
        if show_form_errors:
            response_dict['fields_errors'] = self._fields_errors
        return JsonResponse(response_dict)



class FeedBackView(View):
    def get(self, request):
        callback_form = CallBackForm()
        return render(request, 'main/feedback.html',
                      {'page_name': "Форма обратной связи", 'callback_form': callback_form})

    def post(self, request):
        callback_form = CallBackForm(request.POST)
        response_factory = FormJsonResponseFactory()
        response_factory.add_form(callback_form)

        return response_factory.get_response()

       # if not callback_form.is_valid():
         #   return render(request, 'main/call_back_form.html', {'callback_form': callback_form, 'st':True})

        #send_mail('Zoom: Заявка на обратный звонок', '', 'site_zoom@zoom_photo.ru',
                  #['dvil@mail.ru'], fail_silently=False)

        #return render(request, 'main/call_back_form.html', {'callback_form':  CallBackForm()})


def feedback(request):
    calback_form = CallBackForm()
    return render(request, 'main/feedback.html', {'page_name': "Форма обратной связи", 'callback_form': calback_form})





class PromoView(View):
    def get(self, request):
        promo_form = PromoForm()
        return render(request, 'main/promo.html', {'promo_form': promo_form})

    def post(self, request):
        promo_form = PromoForm(request.POST)

        response_factory = FormJsonResponseFactory()
        response_factory.add_form(promo_form)

        if not promo_form.is_valid():
            return response_factory.get_negative_response([])

        email = promo_form.cleaned_data['email']

        promocode_length = 6
        generator = PromoCodeGeneratorService(length=promocode_length)
        promo_exists_strategy = OnePromoOnePersonStrategy()
        promo_service = PromoSimpleService(generator, promo_exists_strategy)

        promo_name = 'Скидка10%Лето2020'
        promo_expiration_date = datetime.strptime('2020-08-31', '%Y-%m-%d').date()

        try:
            promocode = promo_service.create_promocode(promo_name, email, promo_expiration_date)

        except Exception as PromoExistsError:
            return response_factory.get_negative_response(['Для адреса {} ранее уже был выдан промокод'.format(email), ])

        return response_factory.get_response()



