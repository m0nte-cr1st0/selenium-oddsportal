from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=254)
    telegram = models.CharField(max_length=40, null=True, blank=True)
    is_subscribed = models.BooleanField(default=False)
    send_to_telegram = models.BooleanField(default=False)
    send_to_email = models.BooleanField(default=False)
    oddsportal_username = models.CharField(max_length=40, blank=True, null=True)
    oddsportal_password = models.CharField(max_length=40, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.oddsportal_username:
                if not self.oddsportal_username in Link.objects.values_list('link'):
                    link = Link.objects.create(link=self.oddsportal_username)
                    link.password = self.oddsportal_password
                    link.save()
        else:
            if Link.objects.filter(user__pk=self.pk).exists():
                link = Link.objects.filter(user__pk=self.pk)[0]
                if link:
                    if self.oddsportal_username != link.link:
                        link.link = self.oddsportal_username
                    link.password = self.oddsportal_password
                    link.save()
        super(User, self).save(*args, **kwargs)


RESULT_WON = 'Won'
RESULT_LOSE = 'Lose'

RESULT_CHOICES = (
    (RESULT_WON, 'Won'),
    (RESULT_LOSE, 'Lose')
)


class Link(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, blank=True)
    link = models.CharField(max_length=40, null=True, blank=True)
    password = models.CharField(max_length=40, blank=True, null=True)
    bank = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_bank = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    won = models.PositiveSmallIntegerField(default=0)
    lose = models.PositiveSmallIntegerField(default=0)
    profit_for_month = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        ordering = ['-profit_for_month', '-bank', '-won', 'lose']

    def __str__(self):
        return self.link or self.pk


class Prediction(models.Model):
    link = models.ForeignKey(Link, null=True, on_delete=models.SET_NULL)
    user = models.CharField(max_length=254, blank=True, null=True)
    date = models.DateTimeField()
    sport = models.CharField(max_length=254)
    league = models.CharField(max_length=254)
    teams = models.CharField(max_length=254)
    prediction = models.CharField(max_length=254)
    match_result = models.CharField(max_length=254)
    prediction_result = models.CharField(max_length=10, choices=RESULT_CHOICES, blank=True, null=True)
    link_to_match = models.URLField()
    link_to_odd = models.URLField()
    bet_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bet_coefficient = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date', '-teams']

    def __str__(self):
        return self.teams


class PredictionBK(models.Model):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    name = models.CharField(max_length=254)
    coefficient = models.CharField(max_length=254, blank=True, null=True)

    class Meta:
        ordering = ['coefficient']

