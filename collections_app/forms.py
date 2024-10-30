# collections_app/forms.py
from django import forms
from .models import Collection , Link


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name']


class LinkForm(forms.ModelForm):
    collection = forms.ModelChoiceField(
        queryset=Collection.objects.none(),  # Initially empty
        required=False,
        widget=forms.Select(attrs={'class': 'collection-dropdown'}),
        empty_label=None  # Remove the empty placeholder option
    )
    
    class Meta:
        model = Link
        fields = ['url', 'name', 'description', 'collection']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Retrieve the user
        super().__init__(*args, **kwargs)
        
        # Populate the collection dropdown with user's collections
        if user:
            self.fields['collection'].queryset = Collection.objects.filter(user=user)