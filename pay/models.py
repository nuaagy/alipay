from django.db import models


class Goods(models.Model):
    name = models.CharField(max_length=32)
    price = models.DecimalField(max_digits=8, decimal_places=2)


class Order(models.Model):
    no = models.CharField(max_length=64)
    goods = models.ForeignKey(to='Goods', on_delete=models.CASCADE)
    status_choices = (
        (1, '未支付'),
        (2, '已支付'),
    )
    status = models.SmallIntegerField(choices=status_choices, default=1)
