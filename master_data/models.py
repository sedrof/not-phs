from django.db import models


class FamilySituation(models.Model):
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100, null = True, blank = True)
    def __str__(self):
        return self.display_name or self.name

    def FamilySituation_modify(self):
        if self.name == 'S':
            self.name = 'Single'
        elif self.name == 'SP':
            self.name = 'Single 1-2 kids'
        elif self.name == 'CWC':
            self.name = 'Couple 1-2 kids'
        elif self.name == 'CPL':
            self.name = 'Couple'
        elif self.name == 'OTHER':
            self.name = 'Couple'


class MaintenanceType(models.Model):
    name = models.CharField(max_length=10)
    display_name = models.CharField(max_length=100, null = True, blank = True)    
    def __str__(self):
        return self.display_name or self.name


class Relationship(models.Model):
    name = models.CharField(max_length=20)
    display_name = models.CharField(max_length=100, null = True, blank = True)
    def __str__(self):
        return self.display_name or self.name or ''
