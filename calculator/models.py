from django.db import models
from datetime import date
import datetime
from django.core.validators import MaxValueValidator
from master_data.models import *
from centrelink.models import *
from .calculations import *
from django.db.models import Q
from django.contrib.auth.models import Group, User
from django.utils.html import mark_safe
from django.core.exceptions import ValidationError
from django.urls import reverse, NoReverseMatch
from django.core.exceptions import ImproperlyConfigured




class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    income_period_choices = (('Weekly', 'Weekly'), ('Fortnightly',
                                                    'Fortnightly'))
    chp_reference = models.CharField(max_length=50, unique=True)
    rent_effective_date = models.DateField(null=True, blank=True)
    income_period = models.CharField(max_length=11,
                                     choices=income_period_choices,
                                     null=True,
                                     blank=True, default='Weekly')
    property_market_rent = models.DecimalField(help_text='Weekly',
                                               max_digits=7,
                                               decimal_places=2,
                                               null=True,
                                               blank=True)
    number_of_family_group = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[
            MaxValueValidator(5)])
    cruser = models.CharField(max_length=50, null=True, blank=True)
    prop_id = models.PositiveIntegerField(null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    group = models.OneToOneField(Group,
                                 on_delete=models.CASCADE,
                                 null=True)
    def __str__(self):
        # return 'CHP: ' + str(self.chp_reference)
        return str(self.chp_reference)

    @property
    def cra_rate_from(self):
        f = CraRate.objects.filter(valid_from='2019-12-17')
        for d in f:
            return d.valid_from


    @property
    def ftb_combined(self):
        ftb_combined = 0
        for family_group in self.family_groups.all():
            ftb_combined += family_group.ftb_combined
        return ftb_combined

    

    def clean(self):
        count_fg = self.family_groups.count()

        # if self.number_of_family_group != count_fg:
        #     raise ValidationError(
        #         'Number of family group doesnt match with FG_NO.')
        if self.rent_effective_date is None:
            raise ValidationError('Please enter rent_effective_date.')
        elif not self.chp_reference:
            raise ValidationError('Please enter chp_reference.')
        elif not self.income_period:
            raise ValidationError('Please enter income_period.')
        elif (self.property_market_rent or 0) >= 10000 or (self.property_market_rent or 0) <= 0:
            raise ValidationError(
                'Property Market Rent should be more than 0 and less than 10000')

    @property
    def print_report(self):
        if self.complete:
            try:
                view_link = reverse(
                    'pdf_view', kwargs={
                        'chp_reference': self.chp_reference})
            except (NoReverseMatch, ImproperlyConfigured):
                pass
            try:
                mark_safe_param = '<a href= {} target="_blank" >Print Report</a>'.format(
                    view_link)
            except UnboundLocalError:
                pass
            try:
                return mark_safe(mark_safe_param)
            except UnboundLocalError:
                pass
        return 'Insufficient Info.'
        
    @property    
    def print_pdf(self):
        if self.complete:
            view_link = reverse('pdfss')
            mark_safe_param = '<a href= {} target="_blank" >Print Report</a>'.format(view_link)
            return mark_safe(mark_safe_param)
        return 'Insufficient Info.'
      
    @property
    def last_rent(self):
        a = self.chp_reference
        b = FamilyGroup.objects.filter(
            Q(last_rent__gte=0) & Q(transaction__chp_reference=a))
        if list(b) == []:
            return 0
        for f in b:
            return f.last_rent


    @property
    def sufficient_information_provided(self):
        count_fg = self.family_groups.count()
        return all(
            [
                self.rent_effective_date,
                self.income_period,
                0.00 < (self.property_market_rent or 0) <= 10000,
                self.number_of_family_group,
                self.number_of_family_group == count_fg,

            ]
        )

    @property
    def complete(self):
        if not self.sufficient_information_provided:
            return False
        elif not self.family_groups.all():
            return False
        for f in self.family_groups.all():
            if not f.family_members.all():
                return False
            for m in f.family_members.all():
                if not m.sufficient_information_provided:
                    return False
            if not f.sufficient_information_provided:
                return False
        return True

    @property
    def family_m(self):
        for family in self.fmember.all():
            return family.name, family.age, family.transaction, family.family_group

    @property
    def household_rent(self):
        household_rent = 0
        for family_group in self.family_groups.all():
            household_rent += float(family_group.rent_charged)
        try:
            print(household_rent)
            return min(float(household_rent or 0), (self.property_market_rent or 0))
        except TypeError:
            return 0
        # return "%.2f" % float(household_rent or 0)


    @property
    def cra_compon(self):
        for f in self.family_groups.all():
            return float(f.cra_component or 0)

    @property
    def report(self):
        family_groups = []
        for f in self.family_groups.all():
            family_members = []
            for m in f.family_members.all():
                family_members.append({
                    'name':
                    str(m),
                    'rent_percentage':
                    float(m.effective_rent_percentage or 0),
                    'weekly_income':
                    "%.2f" % float(m.weekly_income or 0),
                    'rent_component':
                    "%.2f" % float(m.income_component or 0)
                })
            family_groups.append({
                str(f): {
                    'family_members':
                    family_members,
                    'additional_income': [{
                        'income_type':
                        'FTB',
                        'rent_percentage':
                        float(f.ftb_rate or 0),
                        'weekly_income':
                        "%.2f" % float(f.ftb_combined or 0),
                        'rent_component':
                        "%.2f" % float(f.ftb_component or 0),
                    }, {
                        'income_type':
                        'CRA',
                        'rent_percentage':
                        float(f.cra_rate or 0),
                        'weekly_income':
                        "%.2f" % float(f.cra_component or 0),
                        'rent_component':
                        "%.2f" % float(f.cra_component or 0),
                    }, {
                        'income_type':
                        'Maintenance',
                        'rent_percentage':
                        float(f.maintenance_rate or 0),
                        'weekly_income':
                        "%.2f" % float(f.weekly_maintenance or 0),
                        'rent_component':
                        "%.2f" % float(f.maintenance_component or 0),
                    }],
                    'rent_charged':
                    "%.2f" % float(f.rent_charged or 0),
                    'last_rent':
                    "%.2f" % float(f.last_rent or 0)
                }
            })
        
        report = [
            family_groups,
            'Household Rent: ' + "%.2f" % float(self.household_rent or 0)
        ]
        return report
        # import json
        # return json.dumps(report, indent=4)
    

class FamilyGroup(models.Model):
    name_choices = (('FG_1', 'FG_1'), ('FG_2', 'FG_2'),
                    ('FG_3', 'FG_3'), ('FG_4', 'FG_4'), ('FG_5', 'FG_5'))
    name = models.CharField(max_length=10, choices=name_choices)
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name='family_groups')
    family_type = models.ForeignKey(FamilySituation,
                                    on_delete=models.PROTECT,
                                    null=True,
                                    blank=True)
    last_rent = models.DecimalField(help_text='per week',
                                    max_digits=7,
                                    decimal_places=2,
                                    null=True,
                                    blank=True)
    any_income_support_payment = models.BooleanField(null=True, blank=True)
    cra_eligibilty = models.BooleanField(help_text='legislated',
                                         null=True,
                                         blank=True)
    cra_amount = models.DecimalField(help_text='per week',
                                     max_digits=6,
                                     decimal_places=2,
                                     null=True,
                                     blank=True)
    ftb_a = models.DecimalField('FTB-A',
                                help_text='Legislated - per week',
                                max_digits=6,
                                decimal_places=2,
                                null=True,
                                blank=True)
    ftb_b = models.DecimalField('FTB-B',
                                help_text='Legislated - per week',
                                max_digits=6,
                                decimal_places=2,
                                null=True,
                                blank=True)
    maintenance_amount = models.DecimalField(max_digits=7,
                                             decimal_places=2,
                                             null=True,
                                             blank=True,
                                             help_text='Per year')
    maintenance_type = models.ForeignKey(
        MaintenanceType,
        on_delete=models.PROTECT,
        limit_choices_to={'name__in': ['Single', 'Couple']},
        null=True,
        blank=True)
    number_of_additional_children = models.IntegerField(null=True, blank=True)
    number_of_family_member = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(20)])

    class Meta:
        unique_together = ['transaction', 'name']

    @property
    def weekly_maintenance(self):
        return float((self.maintenance_amount or 0) * 7 / 365)

    @property
    def rent_assessment_rate(self):
        return RentAssessmentRate.objects.get(active='Yes')

    @property
    def property_market_rent(self):
        d = Transaction.objects.filter(property_market_rent__gte=0)
        for f in d:
            return f.property_market_rent

    @property
    def maximum_cra_payment(self):
        a = self.family_type.name
        f = FamilySituationRate.objects.filter(
            Q(family_situation__name=a)
            & Q(maximum_cra_payment__gte=0))
        for d in f:
            if self.transaction.income_period == 'Weekly':
                return float(d.maximum_cra_payment or 0)
            return (float(d.maximum_cra_payment or 0)) / 2

    @property
    def upper_thershold(self):
        a = self.family_type.name
        f = FamilySituationRate.objects.filter(
            Q(family_situation__name=a)
            & Q(upper_thershold__gte=0))
        for d in f:
            if self.transaction.income_period == 'Weekly':
                return float(d.upper_thershold or 0)
            return (float(d.upper_thershold or 0)) / 2

    @property
    def lower_threshold(self):

        a = self.family_type.name
        f = FamilySituationRate.objects.filter(
            Q(family_situation__name=a)
            & Q(lower_threshold__gte=0)
        )
        for d in f:
            if self.transaction.income_period == 'Weekly':
                return float(d.lower_threshold or 0)
            return (float(d.lower_threshold or 0)) / 2

    @property
    def maintenance_rate_additional_child(self):
        try:
            b = self.maintenance_type.display_name
        except AttributeError:
            b = "No username found!"
        r = MaintenanceTypeRate.objects.filter(
            maintenance_type__display_name__istartswith='addi')
        for f in r:
            return float(f.rate or 0)

    @property
    def additional_child_combined(self):
        return (self.number_of_additional_children
                or 0) * self.maintenance_rate_additional_child

    @property
    def maintenance_type_rate(self):
        try:
            b = self.maintenance_type.display_name
        except AttributeError:
            b = "No username found!"
        r = MaintenanceTypeRate.objects.filter(
            Q(rate__gte=0) & Q(maintenance_type__display_name=b))
        for d in r:
            return float(d.rate or 0)

    @property
    def income_free_area(self):
        return (self.maintenance_type_rate or 0) + \
            self.additional_child_combined

    @property
    def ftb_rate(self):
        return self.rent_assessment_rate.ftb

    @property
    def cra_rate(self):
        return self.rent_assessment_rate.cra

    @property
    def maintenance_rate(self):
        return self.rent_assessment_rate.maintenance

    @property
    def ftb_combined(self):

        return (self.ftb_a or 0) + (self.ftb_b or 0)

    @property
    def ftb_component(self):
        if (self.cra_eligibilty) and (self.ftb_combined > 0) and (
                self.any_income_support_payment) and (self.maintenance_amount):
            return (
                CRA_5(
                    self.lower_threshold,
                    self.upper_thershold,
                    self.maximum_cra_payment,
                    self.transaction.property_market_rent,
                    self.income_component,
                    self.maintenance_amount,
                    self.maintenance_component,
                    self.ftb_a,
                    self.ftb_b,
                    self.adjustable_basket,
                    self.income_free_area,
                    self.last_rent,
                    self.cra_amount))[2]

        elif (self.cra_eligibilty) and (self.ftb_combined > 0) and not (
                self.any_income_support_payment):
            return (
                CRA_6(
                    self.lower_threshold,
                    self.upper_thershold,
                    self.maximum_cra_payment,
                    self.transaction.property_market_rent,
                    self.income_component,
                    self.maintenance_component,
                    self.ftb_a,
                    self.ftb_b,
                    self.adjustable_basket,
                    self.last_rent,
                    self.cra_amount))[2]
        else:
            return self.ftb_combined * self.ftb_rate / 100

    @property
    def maintenance_component(self):
        b = (self.weekly_maintenance or 0) * self.maintenance_rate / 100
        return float(b)

    @property
    def cra_component(self):
        if (self.cra_eligibilty) and (self.ftb_component == 0) and (
                self.any_income_support_payment):
            return (
                CRA_2(
                    self.lower_threshold,
                    self.upper_thershold,
                    self.maximum_cra_payment,
                    self.transaction.property_market_rent,
                    self.income_component,
                    self.maintenance_component,
                    self.last_rent))[0]

        elif (self.cra_eligibilty) and (
                self.ftb_component
                == 0) and not (self.any_income_support_payment):

            return (
                CRA_3(
                    self.lower_threshold,
                    self.upper_thershold,
                    self.maximum_cra_payment,
                    self.transaction.property_market_rent,
                    self.last_rent,
                    self.income_component,
                    self.maintenance_amount,
                    self.cra_amount))[0]
        elif (self.cra_eligibilty) and (self.ftb_component is not None) and (
                self.any_income_support_payment) and (
                    self.maintenance_component == 0):
            return (
                CRA_4(
                    self.lower_threshold,
                    self.upper_thershold,
                    self.maximum_cra_payment,
                    self.transaction.property_market_rent,
                    self.income_component,
                    self.ftb_component,
                    self.last_rent))[0]

        elif (self.cra_eligibilty) and (self.ftb_component is not None) and (
                self.any_income_support_payment) and (self.maintenance_amount >
                                                      0):
            return (
                CRA_5(
                    self.lower_threshold,
                    self.upper_thershold,
                    self.maximum_cra_payment,
                    self.transaction.property_market_rent,
                    self.income_component,
                    self.maintenance_amount,
                    self.maintenance_component,
                    self.ftb_a,
                    self.ftb_b,
                    self.adjustable_basket,
                    self.income_free_area,
                    self.last_rent,
                    self.cra_amount))[0]

        elif (self.cra_eligibilty) and (self.ftb_component is not None) and not (
                self.any_income_support_payment):
            return (
                CRA_6(
                    self.lower_threshold,
                    self.upper_thershold,
                    self.maximum_cra_payment,
                    self.transaction.property_market_rent,
                    self.income_component,
                    self.maintenance_component,
                    self.ftb_a,
                    self.ftb_b,
                    self.adjustable_basket,
                    self.last_rent,
                    self.cra_amount))[0]
        else:
            return (self.cra_amount or 0) * self.cra_rate / 100

    def clean(self):
        super().clean()
        if not self.name:
            raise ValidationError('Enter FG_NO')
        elif not self.family_type:
            raise ValidationError('Enter FamilyType')
        elif not self.last_rent:
            raise ValidationError('Enter Last rent')
        elif (not self.cra_eligibilty and self.cra_amount):
            raise ValidationError('Wrong Cra inputs')
        elif (not self.maintenance_amount and self.number_of_additional_children and not self.maintenance_type)\
                or (self.maintenance_amount and self.maintenance_type and not self.number_of_additional_children)\
                or (self.maintenance_amount and not self.maintenance_type and not self.number_of_additional_children)\
                or (not self.maintenance_amount and self.maintenance_type and not self.number_of_additional_children)\
                or (not self.maintenance_amount and not self.maintenance_type and self.number_of_additional_children)\
                or (not self.maintenance_amount and self.maintenance_type and self.number_of_additional_children):
            raise ValidationError('Wrong Maintenance inputs')
        # elif self.cra_amount < 0
        # elif (self.cra_eligibilty) and (self.cra_amount > (self.cra_last_rent or 0)):
        #     raise ValidationError('Wrong Cra inputs')

    @property
    def sufficient_information_provided(self):
        if not self.name and not self.family_type and not self.last_rent:
            return False
        elif self.maintenance_amount and self.number_of_additional_children and not self.maintenance_type:
            return False
        elif not self.cra_eligibilty and self.cra_amount:
            return False
        elif not self.maintenance_amount and self.number_of_additional_children and not self.maintenance_type:
            return False
        elif self.maintenance_amount and self.maintenance_type and not self.number_of_additional_children:
            return False
        elif self.maintenance_amount and not self.maintenance_type and not self.number_of_additional_children:
            return False
        # elif not self.maintenance_amount and self.maintenance_type and not self.number_of_additional_children:
        #     return False
        elif not self.maintenance_amount and not self.maintenance_type and self.number_of_additional_children:
            return False
        elif not self.maintenance_amount and self.maintenance_type and self.number_of_additional_children:
            return False
        return True

    def __str__(self):
        return self.name

    @property
    def income_component(self):
        income_component = 0
        for family_member in self.family_members.all():
            income_component += family_member.income_component
        return float(income_component)

    @property
    def maximum_ftb_payment(self):
        maximum_ftb_payment = 0
        for family_memeber in self.family_members.all():
            maximum_ftb_payment += family_memeber.maximum_ftb_payment
        return float(maximum_ftb_payment)

    @property
    def ftb_base_rate(self):
        ftb_base_rate = 0
        for family_member in self.family_members.all():
            ftb_base_rate += family_member.ftb_base_rate

        return float(ftb_base_rate)

    @property
    def adjustable_basket(self):
        return self.maximum_ftb_payment - self.ftb_base_rate

    @property
    def num_of_family_groups(self):
        i = self.transaction.pk
        b = FamilyGroup.objects.filter(transaction__pk=i).count()

        return b

    @property
    def rent_charged(self):
        if (self.cra_eligibilty) and (self.ftb_component == 0) and (
                self.any_income_support_payment):

            return (
                CRA_2(
                    self.lower_threshold,
                    self.upper_thershold,
                    self.maximum_cra_payment,
                    self.transaction.property_market_rent,
                    self.income_component,
                    self.maintenance_component,
                    self.last_rent))[2]

        elif (self.cra_eligibilty) and (
                self.ftb_component
                == 0) and not (self.any_income_support_payment):

            return (
                CRA_3(
                    self.lower_threshold,
                    self.upper_thershold,
                    self.maximum_cra_payment,
                    self.transaction.property_market_rent,
                    self.last_rent,
                    self.income_component,
                    self.maintenance_component,
                    self.cra_amount))[2]
        elif (self.cra_eligibilty) and (self.ftb_component is not None) and (
                self.any_income_support_payment) and (
                    self.maintenance_component == 0):

            return (
                CRA_4(
                    self.lower_threshold,
                    self.upper_thershold,
                    self.maximum_cra_payment,
                    self.transaction.property_market_rent,
                    self.income_component,
                    self.ftb_component,
                    self.last_rent))[2]

        elif (self.cra_eligibilty) and (self.ftb_component is not None) and (
                self.any_income_support_payment) and (self.maintenance_amount >
                                                      0):

            return (
                CRA_5(
                    self.lower_threshold,
                    self.upper_thershold,
                    self.maximum_cra_payment,
                    self.transaction.property_market_rent,
                    self.income_component,
                    self.maintenance_amount,
                    self.maintenance_component,
                    self.ftb_a,
                    self.ftb_b,
                    self.adjustable_basket,
                    self.income_free_area,
                    self.last_rent,
                    self.cra_amount))[1]

        elif (self.cra_eligibilty) and (self.ftb_component is not None) and not (
                self.any_income_support_payment):

            return (
                CRA_6(
                    self.lower_threshold,
                    self.upper_thershold,
                    self.maximum_cra_payment,
                    self.transaction.property_market_rent,
                    self.income_component,
                    self.maintenance_component,
                    self.ftb_a,
                    self.ftb_b,
                    self.adjustable_basket,
                    self.last_rent,
                    self.cra_amount))[1]
        else:
            return float(self.income_component) + float(
                self.ftb_component) + float(self.cra_component) + float(
                    self.maintenance_component)


class FamilyMember(models.Model):
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="fmember")
    family_group = models.ForeignKey(FamilyGroup,
                                     on_delete=models.CASCADE,
                                     null=True,
                                     blank=True, related_name='family_members')
    name = models.CharField(max_length=100, null=True, blank=True)
    surname = models.CharField(max_length=100, null=True, blank=True)
    contact_id = models.PositiveIntegerField(
        null=True, blank=True, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    partnered = models.BooleanField(null=True, blank=True)
    relationship = models.ForeignKey(
        Relationship,
        on_delete=models.PROTECT,
        null=True,
        blank=True)
    care_percentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[
            MaxValueValidator(100),
        ])
    income = models.DecimalField(max_digits=6,
                                 decimal_places=2,
                                 null=True,
                                 blank=True,
                                 help_text='''Excluding:
1. Maintenance
2. FTB-A & FTB-B
3. CRA
but incl. ES(1) for all payments and FTB-A & FTB-B''')
    rent_percentage = models.DecimalField(max_digits=6,
                                          decimal_places=2,
                                          null=True,
                                          blank=True)

    @property
    def maximum_ftb_payment(self):
        b = self.relationship
        f = FtbAMaximumPayment.objects.filter(
            Q(maximum_payment__gte=0)
            & Q(dependant_child_age__display_name=b))
        if list(f) == []:
            return 0
        for h in f:
            return h.maximum_payment

    @property
    def ftb_base_rate(self):
        a = self.relationship
        f = FtbAMaximumPayment.objects.filter(
            Q(ftb_rate__ftb_a_base_rate_payments__gte=0)
            & Q(dependant_child_age__display_name=a))
        if list(f) == []:
            return 0
        for h in f:
            return h.ftb_rate.ftb_a_base_rate_payments

    @property
    def effective_rent_percentage(self):
        if self.rent_percentage:
            return self.rent_percentage
        if self.relationship in ['Tenant', 'Partner']:
            return 25
        if (self.age or 0) >= 21:
            return 25
        if (self.age or 0) >= 18 and (self.age or 0) <= 20:
            return 15

    @property
    def income_component(self):
        return float((self.weekly_income or 0) *
                     (self.effective_rent_percentage or 0) / 100)

    @property
    def age(self):
        from math import floor
        if self.date_of_birth:
            return floor(
                (date.today() - self.date_of_birth).days / 365.25)

    def clean(self):
        from django.core.exceptions import ValidationError
        b = ["Tenant", "Partner", "Others"]
        print(self.age)
        if not self.name or not self.date_of_birth or not self.relationship:
            raise ValidationError(
                'Make sure to enter all your personal info, Eg: name/surname B.date / ID')
        elif self.relationship.display_name in b and not self.income:
            raise ValidationError(
                'please enter your income if you are Tenant, Partner or Other')
        
        elif self.age > 20 and self.relationship.display_name not in b:
            raise ValidationError(
                'Wrong inputs in the date of birth/relationship'
            )

    @property
    def sufficient_information_provided(self):
        b = ["Tenant", "Partner", "Others"]
        zero_kids = ["Couple", "Single", "Single Sharer", ]
        two_one_kids = ["Couple, 1-2 kids", "Single, 1-2 kids", ]
        three_kids = ["Couple, 3+ kids", "Single, 3+ kids", ]
        if not self.name or not self.date_of_birth or not self.relationship:
            return False
        elif self.relationship.display_name in b and not self.income:
            return False
        elif self.age > 20 and self.relationship.display_name not in b:
            return False
        return True

    @property
    def weekly_income(self):
        if self.transaction.income_period == 'Weekly':
            return self.income
        return (self.income or 0) / 2

    def __str__(self):
        return str(self.name)
