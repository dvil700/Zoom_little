from django.test import TestCase
from datetime import datetime
from .services import PromoSimpleService, PromoCodeGeneratorService, OnePromoOnePersonStrategy, PromoExistsError


class TestServices(TestCase):
    def test_generator(self):
        length = 6
        generator = PromoCodeGeneratorService(length=length)
        value = generator.generate()
        self.assertEqual(len(value), length)
        value2 = generator.generate()
        self.assertNotEqual(value, value2)
        print('generated values {} {}'.format(value, value2))

    def test_promo_simple_service(self):
        promocode_length = 6
        generator = PromoCodeGeneratorService(length=promocode_length)
        promo_exists_strategy = OnePromoOnePersonStrategy()
        promo_service = PromoSimpleService(generator, promo_exists_strategy)
        promocode = promo_service.create_promocode('xxx', 'dvil@mail.ru', datetime.strptime('2020-08-31', '%Y-%m-%d').date())
        self.assertEqual(len(promocode.promo_code), promocode_length)
        try:
            promocode2 = promo_service.create_promocode('xxx', 'dvil@mail.ru',
                                                       datetime.strptime('2020-08-31', '%Y-%m-%d').date())
            self.assertEqual(True, False, 'Должно было произойти исключение PromoExistsError')
        except Exception as e:
            self.assertEqual(e, PromoExistsError)



