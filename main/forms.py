from django.forms import Form, CharField, TextInput, EmailField

msg_field_required = 'Заполните обязательное поле'


class CallBackForm(Form):
    name = CharField(label='Имя', max_length=30, error_messages={'required': msg_field_required},
                     widget=TextInput(attrs={'placeholder': 'Имя'}))
    phone_number = CharField(label='Телефон', max_length=15, error_messages={'required': msg_field_required},
                             widget=TextInput(attrs={'type': 'tel', 'placeholder': 'Номер телефона'}))


class PromoForm(Form):
    email = EmailField(error_messages={'required': msg_field_required}, widget=TextInput(
                       attrs={'type': 'email', 'placeholder': 'Ваш e-mail', 'aria-label': 'Ваш e-mail'}))





class ReCaptcha(Form):
    captcha_token = CharField(max_length=2000)

