from django.db import models


class Promo(models.Model):
    name = models.CharField(max_length=20, unique=True)


class PromoCodeStorage(models.Model):
    promo = models.ForeignKey(Promo, on_delete=models.CASCADE, db_index=True)
    email = models.EmailField()
    promo_code = models.CharField(max_length=10, unique=True, db_index=True)
    expiration_date = models.DateTimeField()

    class Meta:
        indexes = [models.Index(fields=['promo', 'email']), ]


