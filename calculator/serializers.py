from rest_framework import serializers
from . models import *
from master_data.models import *
from centrelink.models import *


class RentAssessmentRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = RentAssessmentRate
        fields = "__all__"
class FtbAMaximumPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = FtbAMaximumPayment
        fields = "__all__"

class FtbRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = FtbRate
        fields = "__all__"


class MaintenanceTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = MaintenanceType
        fields = "__all__"    


class MaintenanceTypeRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = MaintenanceTypeRate
        fields = "__all__"             

class MaintenanceIncomeTestRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = MaintenanceIncomeTestRate
        fields = "__all__"         
class FamilySituationRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = FamilySituationRate
        fields = "__all__"              

class CraRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CraRate
        fields = "__all__"      

class RelationshipSerializer(serializers.ModelSerializer):

    class Meta:
        model = Relationship
        fields = "__all__"        

    

class FamilySituationSerializer(serializers.ModelSerializer):

    class Meta:
        model = FamilySituation
        fields = "__all__"        


class FamilyMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = FamilyMember
        fields = "__all__"
    # depth = 2

class FamilyGroupSerializer(serializers.ModelSerializer):
    # family_member = FamilyMemberSerializer(many=True, read_only=True, source="family_members")
    class Meta:
        model = FamilyGroup
        fields = "__all__"
        # depth = 1


class TransactionSerializer(serializers.ModelSerializer):
    family_group = FamilyGroupSerializer(
        many=True, read_only=True, source="family_groups")
    family_member = FamilyMemberSerializer(
        many=True, read_only=True, source="fmember")
    # family_group = FamilyGroupSerializer(
    # many=True, source="family_groups")

    class Meta:
        model = Transaction
        fields = ('id', 'income_period', 'chp_reference', 'rent_effective_date', 'property_market_rent', 'number_of_family_group',
                  'cruser', 'prop_id', 'state', 'report' ,'family_group', 'family_member')
    # depth = 1