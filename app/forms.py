from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import Customer, Product,Contact

class CustomerForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = ['username', 'f_name1', 'l_name1', 'email1', 'phone1', 'address1', 'password1', 'password2']
        
    
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        self.fields['password1'].widget.attrs.update({'maxlength': '100'})
        self.fields['password2'].widget.attrs.update({'maxlength': '100'})

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price','quantity_in_stock','description_text', 'image']        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_in_text': forms.TextInput(attrs={'class': 'form-control'}),
            'description_text': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

        # Explicitly styling the ImageField
        self.fields['image'].widget.attrs.update({'class': 'form-control'})


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.TextInput(attrs={'class': 'form-control'}),
            
        }

