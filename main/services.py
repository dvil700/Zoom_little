from abc import ABC, abstractmethod
import random
from django.db import IntegrityError
from .models import Promo, PromoCodeStorage


class PromoCodeGeneratorService:
    def __init__(self, length, symbols: str = None):
        self._length = length
        self._symbols = symbols
        if not symbols:
            self._symbols = self._default_symbols()

    def _default_symbols(self):
        return '1234567890QWERTYUIOPASDFGHJKLZXCVBNM'

    def get_value_list(self):
        return list(self._symbols)

    def generate(self):
        return ''.join([random.choice(self.get_value_list()) for x in range(self._length)])


class PromoExistsError(Exception):
    pass


class PromoExistsStrategy(ABC):
    @abstractmethod
    def execute(self):
        pass


class OnePromoOnePersonStrategy(PromoExistsStrategy):
    def execute(self):
        raise PromoExistsError('Данному польщователю ранее был выдан промокод')


class PromoSimpleService:
    def __init__(self, promo_gen, promo_exists_strategy: PromoExistsStrategy):
        self._promo_gen = promo_gen
        self._promo_exists_strategy = promo_exists_strategy

    def _save_promocode(self, promo, email, exp_date, promo_code):
        for i in range(10):
            try:
                promo_object= PromoCodeStorage(promo=promo, promo_code=promo_code, email=email,
                                                 expiration_date=exp_date)
                promo_object.save()
                return promo_code
            except IntegrityError:
                pass
        raise IntegrityError

    def create_promocode(self, promo_name, email, exp_date):
        promo_code = self._promo_gen.generate()
        try:
            promo = Promo.objects.get(name=promo_name)

        except Promo.DoesNotExist:
            promo = Promo(name=promo_name)
            promo.save()
        try:
            PromoCodeStorage.objects.get(promo=promo, email=email)
            self._promo_exists_strategy.execute()

        except PromoCodeStorage.DoesNotExist:
            return self._save_promocode(promo, email, exp_date, promo_code)
