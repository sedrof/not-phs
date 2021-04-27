from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions
from . serializers import *
from . utils import render_to_pdf
from django.http import HttpResponse
from django.http.response import JsonResponse
from master_data.models import *
from rest_framework.decorators import api_view
from master_data.models import *
from centrelink.models import *
from rest_framework import status
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views import View

@login_required
def ViewPDF(request, *args, **kwargs):
    chp_reference = kwargs.get('chp_reference')
    transaction = get_object_or_404(Transaction, chp_reference=chp_reference)
    print(transaction)
    template_path = 'report-pdf.html'
    context = {"transaction":transaction}
    response = HttpResponse(content_type='Application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('we had some errors' + html )
    return response

@login_required
def pdfs(request, *args, **kwargs):
    transactions = Transaction.objects.all()
    template_path = 'report.html'
    context = {"transactions":transactions}
    response = HttpResponse(content_type='Application/pdf')
    response['Content-Disposition'] = 'filename="reportss.pdf'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('we had some errors' + html )
    return response


@api_view(['GET', ])
def api_transaction(request, chp):
    transaction_serializer = TransactionSerializer()

    transaction = Transaction.objects.filter(chp_reference=chp)
    for r in transaction:
        report = r.report
    if request.method == 'GET':
        if report is not None:
            return JsonResponse(report, safe=False)
        return Response(status=status.HTTP_484_NOT_FOUND)


@api_view(['POST', ])
def post_api(request):
    transaction_serializer = TransactionSerializer(data=request.data)
    transaction_data = request.data
    family_groups = transaction_data["family_group"]
    family_members = transaction_data["family_member"]

    fg_no = len(family_groups)
    fm_no = len(family_members)
    maintenance = []
    ft = []
    rel = []
    """creating an object for Maintenace_type to use in FamilyGroup"""
    for i in range(fg_no):
        if family_groups[i]["maintenance_type"] in ("couple", "COUPLE", "cpl", "CPL", "Cpl"): family_groups[i]["maintenance_type"] = "Couple"
        if family_groups[i]["maintenance_type"] in ("single", "SINGLE", "S", "s"): family_groups[i]["maintenance_type"] = "Single"
        maintenance.append(MaintenanceType.objects.filter(name = family_groups[i]["maintenance_type"]).first())


    """creating an object for Family_Situation to use in FamilyGroup"""
    for i in range(fg_no):
        if family_groups[i]["family_type"] in ("CPL", "couple", "cpl", "c", "C", "COUPLE"):
            family_groups[i]["family_type"] = "Couple"
        if family_groups[i]["family_type"] in ("S", "s", "single", "SINGLE"):
            family_groups[i]["family_type"] = "Single"
        if family_groups[i]["family_type"] in ("SS", "ss", "Ss", "single sharer", "Single sharer", "SINGLE SHARER"):
            family_groups[i]["family_type"] = "Single Sharer"
        if family_groups[i]["family_type"] in ("CPL 1-2", "couple 1-2", "cpl 1-2", "Couple 1-2", "COUPLE 1-2", "Cpl 1-2"):
            family_groups[i]["family_type"] = "Couple 1-2 kids"
        if family_groups[i]["family_type"] in ("CPL 3", "couple 3", "cpl 3", "Couple 3", "COUPLE 3"):
            family_groups[i]["family_type"] = "Couple 3+ kids"
        if family_groups[i]["family_type"] in ("S 1-2", "s 1-2", "single 1-2", "SINGLE 1-2"):
            family_groups[i]["family_type"] = "Single 1-2 kids"
        if family_groups[i]["family_type"] in ("S 3", "s 3", "single 3", "SINGLE 3", "Single 3"):
            family_groups[i]["family_type"] = "Single 3+ kids"
        if family_groups[i]["family_type"] in ("one of couple sep", "One Of Couple Sep",
                                             "one cpl sep", "One CPL sep", "OCS", "ocs", "Ocs"):
            family_groups[i]["family_type"] = "One of a couple sep. due to illness, no dep. Children"
        if family_groups[i]["family_type"] in ("one of couple temp", "One Of Couple Temp",
                                             "one cpl temp", "One CPL temp", "OCT", "oct", "Oct"):
            family_groups[i]["family_type"] = "One of a couple temp. sep., no dep. Children"
        ft.append(FamilySituation.objects.filter(name = family_groups[i]["family_type"]).first())

    """creating an object for Relationship to use in familymember"""
    for i in range(fm_no):
        if family_members[i]["relationship"] in ("partner", "PARTNER",):
            family_members[i]["relationship"] = "Partner"
        if family_members[i]["relationship"] in ("tenant", "TENANT",):
            family_members[i]["relationship"] = "Tenant"
        if family_members[i]["relationship"] in ("dc under 13", "DC UNDER 13", "DC Under 13", "Dc Under 13"):
            family_members[i]["relationship"] = "DC-Under 13"
        if family_members[i]["relationship"] in ("dc 13 15", "dc 13-15",
                                               "DC 13 15", "DC 13-15"):
            family_members[i]["relationship"] = "DC-13-15 years"
        if family_members[i]["relationship"] in ("dc 16 19", "dc 16-19",
                                               "DC 16 19", "DC 16-19"):
            family_members[i]["relationship"] = "16-19 Y Sec. St. or"
        if family_members[i]["relationship"] in ("dc 0 19", "dc 0-19",
                                               "DC 0 19", "DC 0-19"):
            family_members[i]["relationship"] = "DC-In App. Child Care Org 0-19Y"
        if family_members[i]["relationship"] in ("indep child", "INDEP CHILD",
                                               "Indep Child"):
            family_members[i]["relationship"] = "Indep. Child"
        rel.append(Relationship.objects.filter(name=family_members[i]["relationship"]).first())

    """saving the post request data into a Transaction Object"""
    new_transaction = Transaction(chp_reference=transaction_data['chp_reference'],
                                                 income_period=transaction_data['income_period'],
                                                 property_market_rent=transaction_data['property_market_rent'],
                                                 number_of_family_group=transaction_data['number_of_family_group'],
                                                 rent_effective_date=transaction_data['rent_effective_date'],
                                                 state=transaction_data['state'])
    new_transaction.save()

    fg_objs = []
    for i in range(fg_no):

        """the requested data must be in a from of True or False"""
        if family_groups[i]['cra_eligibilty'] in ('Yes', 'yes', 'true', "TRUE"):
            family_groups[i]['cra_eligibilty'] = 'True'
        else:
            family_groups[i]['cra_eligibilty'] = 'False'
        if family_groups[i]['any_income_support_payment'] in ('Yes', 'yes', 'true', "TRUE") :
            family_groups[i]['any_income_support_payment'] = 'True'
        else:
            family_groups[i]['any_income_support_payment'] = 'False'

        """saving the post request data.FamilyGroup into a FamilyGroup Object"""
        c = FamilyGroup(name=family_groups[i]["name"], transaction=new_transaction,
                        last_rent=family_groups[i]["last_rent"], family_type=ft[i],
                        any_income_support_payment=family_groups[i]["any_income_support_payment"],
                        cra_eligibilty=family_groups[i]["cra_eligibilty"], cra_amount=family_groups[i]["cra_amount"],
                        ftb_a=family_groups[i]["ftb_a"], ftb_b=family_groups[i]["ftb_b"], maintenance_amount=family_groups[i]["maintenance_amount"],
                        maintenance_type=maintenance[i], number_of_additional_children= family_groups[i]["number_of_additional_children"])
        c.save()
        fg_objs.append(c)

    for i in range(fm_no):
        if family_members[i]["partnered"] in ('Yes', 'yes', 'true', 'TRUE'):
            family_members[i]["partnered"] = 'True'
        else:
            family_members[i]["partnered"] = 'False'

        j = int(family_members[i]["family_group"][-1]) -1
        """saving the post request data.FamiyMember into a FamilyMember Object"""
        b = FamilyMember(transaction=new_transaction,
                         family_group=fg_objs[j], name=family_members[i]["name"], surname=family_members[i]["surname"],
                         date_of_birth=family_members[i]["date_of_birth"],
                         partnered=family_members[i]["partnered"], relationship=rel[i], care_percentage=family_members[i]["care_percentage"],
                         income=family_members[i]["income"], rent_percentage=family_members[i]["rent_percentage"])
        b.save()


    return Response(status=status.HTTP_201_CREATED)




