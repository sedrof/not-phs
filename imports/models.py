

from django.db import models
from master_data.models import *
from centrelink.models import *
from calculator.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver

class Batch(models.Model):
    income_period_choices = (('Weekly', 'Weekly'),
                             ('Fortnightly', 'Fortnightly'))
    batch = models.CharField(max_length=50)
    transaction_chp_reference = models.CharField(
        max_length=50, null=True, blank=True)
    transaction_rent_effective_date = models.DateField(null=True, blank=True)
    transaction_income_period = models.CharField(
        max_length=11, choices=income_period_choices, null=True, blank=True)
    transaction_property_market_rent = models.DecimalField(
        help_text='Weekly', max_digits=7, decimal_places=2, null=True, blank=True)
    transaction_number_of_family_group = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(5), ])
    transaction_cruser = models.CharField(max_length=50, null=True, blank=True)
    transaction_prop_id = models.PositiveIntegerField(null=True, blank=True)
    transaction_state = models.CharField(max_length=50, null=True, blank=True)
    family_group_name = models.CharField(max_length=100, null=True, blank=True)
    family_group_family_type = models.CharField(
        max_length=50, null=True, blank=True)
    family_group_last_rent = models.DecimalField(
        help_text='per week', max_digits=7, decimal_places=2, null=True, blank=True)
    family_group_any_income_support_payment = models.BooleanField(
        null=True, blank=True)
    family_group_cra_eligibilty = models.BooleanField(
        help_text='legislated', null=True, blank=True)
    family_group_cra_amount = models.DecimalField(
        help_text='per week', max_digits=6, decimal_places=2, null=True, blank=True)
    family_group_ftb_a = models.DecimalField(
        'FTB-A', help_text='Legislated - per week', max_digits=6, decimal_places=2, null=True, blank=True)
    family_group_ftb_b = models.DecimalField(
        'FTB-B', help_text='Legislated - per week', max_digits=6, decimal_places=2, null=True, blank=True)
    family_group_maintenance_amount = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True, help_text='Per year')
    family_group_maintenance_type = models.CharField(
        max_length=50, null=True, blank=True)
    family_group_number_of_additional_children = models.IntegerField(
        null=True, blank=True)
    family_member_name = models.CharField(
        max_length=100, null=True, blank=True)
    family_member_contact_id = models.PositiveIntegerField(null=True, blank=True)
    family_member_surname = models.CharField(max_length=100, null=True, blank=True)
    family_member_partnered = models.BooleanField(null=True, blank=True)
    family_member_date_of_birth = models.DateField(null=True, blank=True)
    family_member_relationship = models.CharField(
        max_length=50, null=True, blank=True)
    family_member_care_percentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(100), ])
    family_member_income = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True)
    family_member_rent_percentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(100), ])
    message = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = 'Import'
        verbose_name_plural = 'Import'
    def __str__(self):
        return str(self.batch)



    def save(self, *args, **kwargs):
        self.message = ''

        """ Family_Type object Input Probabilities """
        if self.family_group_family_type in ("CPL", "couple", "cpl", "c", "C", "COUPLE"):
            self.family_group_family_type = "Couple"
        if self.family_group_family_type in ("S", "s", "single", "SINGLE"):
            self.family_group_family_type = "Single"
        if self.family_group_family_type in ("SS", "ss", "Ss", "single sharer", "Single sharer", "SINGLE SHARER"):
            self.family_group_family_type = "Single Sharer"
        if self.family_group_family_type in ("CPL 1-2", "couple 1-2", "cpl 1-2", "Couple 1-2", "COUPLE 1-2"):
            self.family_group_family_type = "Couple 1-2 kids"
        if self.family_group_family_type in ("CPL 3", "couple 3", "cpl 3", "Couple 3", "COUPLE 3"):
            self.family_group_family_type = "Couple 3+ kids"
        if self.family_group_family_type in ("S 1-2", "s 1-2", "single 1-2", "SINGLE 1-2"):
            self.family_group_family_type = "Single 1-2 kids"
        if self.family_group_family_type in ("S 3", "s 3", "single 3", "SINGLE 3"):
            self.family_group_family_type = "Single 3+ kids"
        if self.family_group_family_type in ("one of couple sep", "One Of Couple Sep",
                                             "one cpl sep", "One CPL sep", "OCS", "ocs", "Ocs"):
            self.family_group_family_type = "One of a couple sep. due to illness, no dep. Children"
        if self.family_group_family_type in ("one of couple temp", "One Of Couple Temp",
                                             "one cpl temp", "One CPL temp", "OCT", "oct", "Oct"):
            self.family_group_family_type = "One of a couple temp. sep., no dep. Children"

        """ Relationship object Input Probabilities """
        if self.family_member_relationship in ("partner", "PARTNER",):
            self.family_member_relationship = "Partner"
        if self.family_member_relationship in ("tenant", "TENANT",):
            self.family_member_relationship = "Tenant"
        if self.family_member_relationship in ("dc under 13", "DC UNDER 13", "DC Under 13", "Dc Under 13"):
            self.family_member_relationship = "DC-Under 13"
        if self.family_member_relationship in ("dc 13 15", "dc 13-15",
                                               "DC 13 15", "DC 13-15"):
            self.family_member_relationship = "DC-13-15 years"
        if self.family_member_relationship in ("dc 16 19", "dc 16-19",
                                               "DC 16 19", "DC 16-19"):
            self.family_member_relationship = "16-19 Y Sec. St. or"
        if self.family_member_relationship in ("dc 0 19", "dc 0-19",
                                               "DC 0 19", "DC 0-19"):
            self.family_member_relationship = "DC-In App. Child Care Org 0-19Y"
        if self.family_member_relationship in ("indep child", "INDEP CHILD",
                                               "Indep Child"):
            self.family_member_relationship = "Indep. Child"

        if self.transaction_chp_reference:
            trans, created = Transaction.objects.update_or_create(
                # filter on the unique value of `chp_reference`
                chp_reference=self.transaction_chp_reference,
                # update these fields, or create a new object with these values
                defaults={
                        # 'chp_reference' : self.transaction_chp_reference,
                        'income_period':self.transaction_income_period,
                        'property_market_rent':self.transaction_property_market_rent,
                        'number_of_family_group':self.transaction_number_of_family_group,
                        'rent_effective_date':self.transaction_rent_effective_date,
                        'cruser':self.transaction_cruser,
                        'prop_id':self.transaction_prop_id,
                        'state':self.transaction_state,
                }
            )
            trans.save()
            self.message += 'Transaction "' + str(trans.chp_reference) + '" Created\n'
            mt = MaintenanceType.objects.filter(
                      name=self.family_group_maintenance_type).first()
            if mt:
                ft = FamilySituation.objects.filter(
                          name=self.family_group_family_type).first()
                if ft:
                    fg, created = FamilyGroup.objects.update_or_create(
                        transaction=trans,
                        name= self.family_group_name,
                        defaults={
                            'cra_amount':self.family_group_cra_amount,
                            'cra_eligibilty':self.family_group_cra_eligibilty,
                            'family_type':ft,
                            'any_income_support_payment': self.family_group_any_income_support_payment,
                            'ftb_a':self.family_group_ftb_a,
                            'ftb_b':self.family_group_ftb_b,
                            'last_rent':self.family_group_last_rent,
                            'maintenance_amount':self.family_group_maintenance_amount,
                            'maintenance_type':mt,
                            'name':self.family_group_name,
                            'number_of_additional_children':self.family_group_number_of_additional_children,
                        }
                    )
                    fg.save()
                    self.message += 'Family Group "' + str(fg.name) + '" Created\n'
                    r = Relationship.objects.filter(
                               name=self.family_member_relationship).first()
                    if r:
                        fm, created = FamilyMember.objects.update_or_create(
                            # transaction=trans,
                            contact_id=self.family_member_contact_id,
                            family_group= fg,
                            defaults={
                                # 'contact_id' : self.family_member_contact_id,
                                # 'transaction' : trans,
                                # 'family_group' : fg,
                                'relationship' : r,
                                'name': self.family_member_name,
                                'care_percentage' : self.family_member_care_percentage,
                                'date_of_birth' : self.family_member_date_of_birth,
                                'income' : self.family_member_income,
                                'rent_percentage' : self.family_member_rent_percentage,
                                'surname' : self.family_member_surname,
                                'partnered' : self.family_member_partnered,

                            }
                        )
                        fm.save()
                        self.message += 'Family Member "' + str(fm.name) + '" Created\n'
                    else:
                        self.message += 'Incorrect relationship \n'
                else:
                    self.message += 'Incorrect Family Type \n'
            else:
                self.message += 'incorrect FamilySituation \n'
        else:
            self.message += 'Incorrect chp_reference \n'
        super(Batch, self).save(*args, **kwargs)

