from import_export.admin import ImportExportModelAdmin, ExportMixin
from django.contrib import admin
from master_data.models import *
from centrelink.models import *
from calculator.models import *
from imports.models import *
from django.utils.safestring import mark_safe
from json2html import *
from django.contrib.auth.models import Group, User
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from import_export import resources




class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = []

    # Add the users field.
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('users', False)
    )

    def __init__(self, *args, **kwargs):
        # Do the normal form initialisation.
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        # If it is an existing group (saved objects have a pk).
        if self.instance.pk:
            # Populate the users field with the current Group users.
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        # Add the users to the Group.
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        # Default save
        instance = super(GroupAdminForm, self).save()
        # Save many-to-many data
        self.save_m2m()
        return instance


admin.site.unregister(Group)


class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ['permissions']


# Register the new Group ModelAdmin.
admin.site.register(Group, GroupAdmin)

admin.site.site_header = 'CRA Calculator'
admin.site.index_title = 'CRA Calculator'
admin.site.site_title = 'CRA Calculator'


class FamilyGroupInline(admin.TabularInline):
    model = FamilyGroup
    extra = 0

    def sufficient_info_provided(self, obj):
        return obj.sufficient_information_provided
    sufficient_info_provided.boolean = True

    def complete(self, obj):
        return obj.complete
    complete.boolean = True

    fieldsets = (
        # (None, {
        #     'fields': ('complete',),
        # }),
        ('FamilyGroup Details', {
            'fields': ('name', 'family_type', 'last_rent', 'any_income_support_payment',
                'cra_eligibilty', 'cra_amount', 'ftb_a', 'ftb_b', 'maintenance_amount', 
                        'maintenance_type', 'number_of_additional_children', 'sufficient_info_provided'),
        }),)
    readonly_fields = ['sufficient_info_provided', 'complete', ]


class FamilyMemberInline(admin.TabularInline):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        action = request.META['PATH_INFO'].strip('/').split('/')[-1]
        if action == 'change':
            transaction_id = request.META['PATH_INFO'].strip(
                '/').split('/')[-2]
            if db_field.name == "family_group":
                kwargs["queryset"] = FamilyGroup.objects.filter(
                    transaction=transaction_id)
        return super(FamilyMemberInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
    model = FamilyMember
    extra = 0

    def sufficient_info_provided(self, obj):
        return obj.sufficient_information_provided
    sufficient_info_provided.boolean = True

    def age(self, obj):
        return obj.age

    fields = ['family_group', 'name', 'date_of_birth', 'age', 'relationship',
              'care_percentage', 'income', 'rent_percentage', 'sufficient_info_provided', ]
    readonly_fields = ['age', 'sufficient_info_provided', ]


class FamilySituationRateInline(admin.TabularInline):
    model = FamilySituationRate
    extra = 0


class FtbAMaximumPaymentInline(admin.TabularInline):
    model = FtbAMaximumPayment
    extra = 0


class MaintenanceTypeRateInline(admin.TabularInline):
    model = MaintenanceTypeRate
    extra = 0

# class TemplateAdmin(admin.ModelAdmin):
#     ...
#     change_form_template = 'admin/preview_template.html'

# custom_admin_site.register(models.Template, TemplateAdmin)
class  TransactionResource(resources.ModelResource):
    class Meta:
        model = Transaction

@ admin.register(Transaction)
class TransactionAdmin(ExportMixin, admin.ModelAdmin):
    # search_fields = ['chp_reference', 'familymember__name']
    inlines = [FamilyGroupInline, FamilyMemberInline]

    def save_model(self, request, obj, form, change):
        # obj.group = request.user.groups.all()
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # return qs.filter(user__groups__user=request.user)
        return qs.filter(user__groups=request.user.groups.first())


        qs = super().get_queryset(request)
        # print(qs)
        transaction = qs
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

    def complete(self, obj):
        return obj.complete
    complete.boolean = True

    def last_rent(self, obj):
        if obj.complete:
            return obj.last_rent
        return None



    def household_rent(self, obj):
        if obj.complete:
            return "%.2f" % float(obj.household_rent)
        return None

    def report(self, obj):
        # if obj.complete:
        return mark_safe(json2html.convert(json=obj.report, table_attributes="class=\"results\" style=\"overflow-x:auto;\""))
        # return 0
    def fm_income(self,obj):
        return obj.fm_income

    def export_csv(modeladmin, request, queryset):
        import csv
        from django.utils.encoding import smart_str
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Report.csv'
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))
        writer.writerow([
            smart_str(u"chp_referene"),
            smart_str(u"Name"),
            smart_str(u"contact_id"),
            smart_str(u"date_of_birth"),
            smart_str(u"age"),
            smart_str(u"Relationship"),
            smart_str(u"Income"),
            smart_str(u"property_market_rent"),
            smart_str(u"FG_Name"),
            smart_str(u"last_rent"),
            smart_str(u"Family_type"),
            smart_str(u"any_income_support_payment"),
            smart_str(u"cra_eligibilty"),
            smart_str(u"cra_amount"),
            smart_str(u"ftb_a"),
            smart_str(u"ftb_b"),
            smart_str(u"maintenance_amount"),
            smart_str(u"maintenance_type"),
            smart_str(u"maintenance_amount"),
            smart_str(u"number_of_additional_children"),
            smart_str(u"rent_effective_date"),
            smart_str(u"income_period"),
            smart_str(u"number_of_family_group"),
            smart_str(u"cruser"),
            smart_str(u"prop_id"),
            smart_str(u"state"),
            smart_str(u"CRA"),
            smart_str(u"household_rent"),
        ])
        for obj in queryset:
            for fm in obj.fmember.all():
                if obj.complete:
                    writer.writerow([
                        smart_str(obj.chp_reference),
                        smart_str(fm.name),
                        smart_str(fm.contact_id),
                        smart_str(fm.date_of_birth),
                        smart_str(fm.age),
                        smart_str(fm.relationship),
                        smart_str(fm.income),
                        smart_str(obj.property_market_rent),
                        smart_str(fm.family_group),
                        smart_str(fm.family_group.last_rent),
                        smart_str(fm.family_group.family_type),
                        smart_str(fm.family_group.any_income_support_payment),
                        smart_str(fm.family_group.cra_eligibilty),
                        smart_str(fm.family_group.cra_amount),
                        smart_str(fm.family_group.ftb_a),
                        smart_str(fm.family_group.ftb_b),
                        smart_str(fm.family_group.maintenance_amount),
                        smart_str(fm.family_group.maintenance_type),
                        smart_str(fm.family_group.maintenance_amount),
                        smart_str(fm.family_group.number_of_additional_children),
                        smart_str(obj.rent_effective_date),
                        smart_str(obj.income_period),
                        smart_str(obj.number_of_family_group),
                        smart_str(obj.cruser),
                        smart_str(obj.prop_id),
                        smart_str(obj.state),
                        smart_str(obj.cra_compon),
                        smart_str(obj.household_rent),
                    ])
                elif not obj.complete:
                    writer.writerow([
                        smart_str(obj.chp_reference),
                        smart_str('ERROR' ),
                        smart_str('IN THE'),
                        smart_str('INPUTS'),
                        smart_str('PLEASE GO'),
                        smart_str('BACK TO THE'),
                        smart_str('APP AND '),
                        smart_str('CORRECT IT'),
                    ])
                writer.writerows([])
        return response
    export_csv.short_description = u"Export CSV"
    


    fieldsets = (
        (None, {
            'fields': ('complete',),
        }),
        ('Transaction Details', {
            'fields': ('chp_reference', 'income_period', 'property_market_rent', 'rent_effective_date', 
                'number_of_family_group','state',),
        }),
        ('Result', {
            'classes': ('collapse',),
            'fields': ('report', 'print_report'),
        }),
    )

    readonly_fields = ['report', 'complete', 'last_rent', 'print_report']
    list_display = ['chp_reference', 'complete', 'income_period', 'last_rent',
                    'household_rent', 'property_market_rent', 'rent_effective_date', 'print_report',]
    display_text = ['Result']
    search_fields = ['chp_reference', 'user__username']
    actions = [export_csv,]

@ admin.register(
    FamilySituation,
    MaintenanceType,
    Relationship,
)
class CraAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass


@ admin.register(RentAssessmentRate)
class RentAssessmentRateAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_editable = ['cra', 'ftb', 'maintenance', 'active']
    list_display = ['name', 'cra', 'ftb', 'maintenance', 'active']


@ admin.register(CraRate)
class CraRateAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    inlines = [FamilySituationRateInline, ]


@ admin.register(FtbRate)
class FtbRateAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    inlines = [FtbAMaximumPaymentInline, ]


@ admin.register(MaintenanceIncomeTestRate)
class MaintenanceIncomeTestRateAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    inlines = [MaintenanceTypeRateInline, ]


@ admin.register(

    FamilySituationRate,
    FtbAMaximumPayment,
    MaintenanceTypeRate,
)
class CraAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}


@ admin.register(Batch)
class BatchAdmin(ImportExportModelAdmin):
    def has_change_permission(self, request, obj=None):
        return None

    def has_add_permission(self, request, obj=None):
        return None

    # list_display = ['batch', 'transaction_chp_reference',
    #                 'family_group_name', 'family_member_name', 'message']

    list_display = ['batch', 'transaction_chp_reference', 'message',]



# from django_otp import OTP_HOTP
# admin.site.unregister(OTP_HOTP)
