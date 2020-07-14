from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from .forms import CallBackForm, PromoForm
from django.views import View
from .services import PromoSimpleService, PromoCodeGeneratorService, OnePromoOnePersonStrategy, PromoExistsError
from django.core.mail import send_mail
from datetime import datetime
from .captcha import recaptcha_site_key, re_captcha_dec, get_captcha_src

# Create your views here.

def index(request):
    return render(request, 'main/index.html', {})


def about(request):
    return render(request, 'main/about.html', {'page_name': "О нас"})


def contact(request):
    return render(request, 'main/contact.html', {'page_name': "Контакты"})


class FormJsonResponseFactory:
    def __init__(self):
        self._fields_errors = []

    def _get_form_errors(self, form):
        for field in form:
            for error in field.errors:
                self._fields_errors.append(dict(id=field.id_for_label, error=error))

    def add_field_error(self, field_id, msg):
        self._fields_errors.append(dict(id=field_id, error=msg))

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

    def get_negative_response(self, errors: list = [], show_form_errors=True):
        response_dict = dict(result=False, general_errors=errors, fields_errors=[])
        if show_form_errors:
            response_dict['fields_errors'] = self._fields_errors
        return JsonResponse(response_dict)


class FeedBackView(View):
    def get(self, request):
        callback_form = CallBackForm()
        return render(request, 'main/feedback.html',
                      {'page_name': "Форма обратной связи", 'callback_form': callback_form,
                       'recaptcha_site_key': recaptcha_site_key})

    @re_captcha_dec
    def post(self, request):
        callback_form = CallBackForm(request.POST)
        response_factory = FormJsonResponseFactory()
        response_factory.add_form(callback_form)

        if not callback_form.is_valid():
            return response_factory.get_negative_response()

        message = 'Обратный звонок. Имя: {name}, Телефон: {phone_number}'.format(**callback_form.cleaned_data)

        send_mail('Zoom: Заявка на обратный звонок', message, 'fzoom34@mail.ru',
                 ['fzoom34@mail.ru'], fail_silently=False)

        return response_factory.get_response()



def photo(request):
    promo_form = PromoForm()
    return render(request, 'main/photo.html', {'page_name': "Фото на документы", 'promo_form': promo_form,
                                                'recaptcha_site_key': recaptcha_site_key})


class PromoView(View):
    @re_captcha_dec
    def post(self, request):
        promo_form = PromoForm(request.POST)

        response_factory = FormJsonResponseFactory()
        response_factory.add_form(promo_form)

        if not promo_form.is_valid():
            return response_factory.get_negative_response()

        email = promo_form.cleaned_data['email']

        promocode_length = 6
        generator = PromoCodeGeneratorService(length=promocode_length)
        promo_exists_strategy = OnePromoOnePersonStrategy()
        promo_service = PromoSimpleService(generator, promo_exists_strategy)

        promo_name = 'Скидка10%Лето2020'
        promo_expiration_date = datetime.strptime('2020-08-31', '%Y-%m-%d').date()

        try:
            promocode = promo_service.create_promocode(promo_name, email, promo_expiration_date)

        except PromoExistsError:
            response_factory.add_field_error(promo_form['email'].id_for_label,
                                             'Для адреса {} ранее уже был выдан промокод'.format(email))

            return response_factory.get_negative_response()
        message = '''Ваш опромокод для получения скидки на фото услуги: {}.
            Промокод возможно использовать только один раз. Срок действия промокода до {}. 
            '''.format(promocode, promo_expiration_date.strftime('%d.%m.%Y'))
        send_mail('foto-zoom34: Промокод', message, 'fzoom34@mail.ru', [email], fail_silently=False)

        return response_factory.get_response()



