from django.db import models
from master_data.models import *
from django.core.validators import MaxValueValidator


class CraRate(models.Model):
    valid_from = models.DateField()
    valid_to = models.DateField()
    def __str__(self):
        return str(self.valid_from) + ' - ' + str(self.valid_to)
    class Meta:
        verbose_name = 'CRA Rate'


class FamilySituationRate(models.Model):
    cra_rate = models.ForeignKey(CraRate,on_delete=models.CASCADE)
    family_situation = models.ForeignKey(FamilySituation,on_delete=models.CASCADE)
    maximum_cra_payment = models.DecimalField(max_digits=6, decimal_places=2)
    lower_threshold = models.DecimalField(max_digits=6, decimal_places=2)
    upper_thershold = models.DecimalField(max_digits=6, decimal_places=2)
    def maximum_cra_payment_weekly(self):
        return self.maximum_cra_payment/2
    def lower_threshold_weekly(self):
        return self.lower_threshold/2
    def upper_thershold_weekly(self):
        return self.upper_thershold/2
    def __str__(self):
        return str(self.family_situation) + ' : ' + str(self.cra_rate)


class MaintenanceIncomeTestRate(models.Model):
    valid_from = models.DateField()
    valid_to = models.DateField()
    def __str__(self):
        return str(self.valid_from) + ' - ' + str(self.valid_to)


class MaintenanceTypeRate(models.Model):
    maintenance_income_test_rate = models.ForeignKey(MaintenanceIncomeTestRate,on_delete=models.CASCADE)
    maintenance_type = models.ForeignKey(MaintenanceType,on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=6, decimal_places=2)
    def __str__(self):
        return str(self.maintenance_type) + ' : ' + str(self.maintenance_income_test_rate)

class FtbRate(models.Model):
    valid_from = models.DateField()
    valid_to = models.DateField()
    ftb_supplement = models.DecimalField(max_digits=9, decimal_places=2)
    income_free_area = models.DecimalField(max_digits=9, decimal_places=2)
    maximum_income = models.DecimalField(max_digits=9, decimal_places=2)
    additional_income_per_child = models.DecimalField(max_digits=9, decimal_places=2)
    ftb_a_base_rate_payments = models.DecimalField(max_digits=9, decimal_places=2)
    large_family_supplement = models.DecimalField(max_digits=9, decimal_places=2, null = True, blank = True)
    class Meta:
        verbose_name = 'FTB Rate'
    def __str__(self):
        return str(self.valid_from) + ' - ' + str(self.valid_to)

class FtbAMaximumPayment(models.Model):
    ftb_rate = models.ForeignKey(FtbRate,on_delete=models.CASCADE)
    dependant_child_age = models.ForeignKey(Relationship,on_delete=models.CASCADE)
    maximum_payment = models.DecimalField(max_digits=6, decimal_places=2)
    class Meta:
        verbose_name = 'FTB-A Maximum Payment'
    def __str__(self):
        return str(self.dependant_child_age.name) + ' : ' + str(self.ftb_rate)

class RentAssessmentRate(models.Model):
    name = models.CharField(max_length=10)
    ftb = models.PositiveSmallIntegerField(null=True, blank=True,validators=[MaxValueValidator(100), ])
    maintenance = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(100), ])
    cra = models.PositiveSmallIntegerField(null=True, blank=True,validators=[MaxValueValidator(100),])
    active = models.CharField('Active Status',max_length=10, choices = (('Yes', 'Yes'),), unique = True, null=True, blank=True)
    def __str__(self):
        return self.name
