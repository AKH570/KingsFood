from django import forms
from .models import PizzaSale, PizzaProfitData
from django.core.exceptions import ValidationError
from datetime import date

class pizzaSaleDataForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set a fixed initial value for the entity and make it read-only
        self.initial['entity'] = 'Kings Confectionery'
        self.fields['entity'].widget.attrs['readonly'] = True
        self.fields['entity'].label = "Entity Name"

        # Remove the default '0' from the form fields for a cleaner UI
        if not self.instance.pk:
            self.initial['FMP_sale'] = ''
            self.initial['foodpanda'] = ''

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-input'})

    class Meta:
        model = PizzaSale
        fields = ['entity', 'FMP_sale', 'foodpanda', 'create_date']
        widgets = {
            'create_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'FMP_sale': 'Net Sale',
            'foodpanda': 'Fpanda Sale',
        }


from django import forms
from django.core.exceptions import ValidationError
from datetime import date

from .models import PizzaProfitData


class pizzaProfitDataForm(forms.ModelForm):

    # ✅ Explicitly define month field to accept YYYY-MM
    month = forms.DateField(
        input_formats=['%Y-%m'],
        widget=forms.DateInput(attrs={
            'type': 'month',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Add form-control class to remaining fields
        for field_name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')

        # ✅ Disburse date input
        self.fields['disburseDate'].widget.attrs.update({'type': 'date'})

        # ✅ Remarks textarea
        self.fields['remarks'].widget = forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter any additional remarks...'
        })

        # ✅ Default status
        if not self.instance.pk:
            self.initial['status'] = 'Given'

    def clean_month(self):
        month = self.cleaned_data.get('month')

        if month:
            # ✅ Always normalize to first day of month
            month = month.replace(day=1)

            # ✅ Prevent future months
            if month > date.today().replace(day=1):
                raise ValidationError("Cannot add data for future months.")

            # ✅ Duplicate month check (year + month)
            if not self.instance.pk:
                if PizzaProfitData.objects.filter(
                    month__year=month.year,
                    month__month=month.month
                ).exists():
                    raise ValidationError(
                        f"An entry for {month.strftime('%B %Y')} already exists."
                    )

        return month

    def clean_distributionAmount(self):
        amount = self.cleaned_data.get('distributionAmount')
        if amount is not None and amount < 0:
            raise ValidationError("Distribution amount cannot be negative.")
        return amount

    def clean_totalProfitAmount(self):
        amount = self.cleaned_data.get('totalProfitAmount')
        if amount is not None and amount < 0:
            raise ValidationError("Total profit amount cannot be negative.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        distribution = cleaned_data.get('distributionAmount')
        total = cleaned_data.get('totalProfitAmount')

        if distribution is not None and total is not None:
            if distribution > total:
                self.add_error(
                    'distributionAmount',
                    "Distribution amount cannot be greater than total profit."
                )

        return cleaned_data

    class Meta:
        model = PizzaProfitData
        fields = [
            'month',
            'totalProfitAmount',
            'distributionAmount',
            'disburseDate',
            'status',
            'remarks',
        ]
        labels = {
            'totalProfitAmount': 'Total Profit Amount',
            'distributionAmount': 'Distribution Amount',
            'disburseDate': 'Disburse Date',
        }
