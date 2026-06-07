from django import forms
from orders.forms import OrderForm
from store.forms import ReviewForm
from accounts.forms import RegistrationForm, AccountCreationForm, UserProfileForm
from orders.models import Payment
from greatkart.validators import *

class PaymentRequestForm(forms.ModelForm):      
    class Meta:
        model = Payment
        first_name = forms.CharField(validators=[validate_only_alphabtes])
        last_name = forms.CharField(validators=[validate_only_alphabtes])
        email = forms.EmailField
        mobile_phone = forms.CharField(validators=[validate_only_numbers])
        address_line_1 = forms.CharField(validators=[validate_special_char])
        address_line_2 = forms.CharField(validators=[validate_special_char])
        city = forms.CharField(validators=[validate_special_char])
        state = forms.CharField(validators=[validate_special_char])
        country = forms.CharField(validators=[validate_special_char])
        zipcode = forms.CharField(validators=[validate_special_char])
        year_grad = forms.CharField(validators=[validate_only_numbers])
        dept = forms.CharField(validators=[validate_only_alphabtes])
        comments = forms.CharField(validators=[validate_special_char])
        exclude = ['udf1', 'udf2', 'udf3', 'udf4', 'udf5', 'checksum', 'req_date', 'txn_status', 'txn_updt_dt' ]   