from django import forms
from application.forms import ChildminderForms
from application.widgets.ConditionalPostChoiceWidget import ConditionalPostInlineRadioSelect


class PITHOwnChildrenCheckForm(ChildminderForms):
    choice_field_name = 'children_in_home'
    auto_replace_widgets = True

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )

    reveal_conditionally = {'known_to_social_services_pith': {'True': 'reasons_known_to_social_services_pith'}}

    known_to_social_services_pith = forms.ChoiceField(
        label='Are you known to council social services in regards to your own children?',
        choices=options,
        widget=ConditionalPostInlineRadioSelect,
        required=False,
        error_messages={
            'required': 'Please say if you are known to council social services in regards to your own children'})

    reasons_known_to_social_services_pith = forms.CharField(
        label='Tell us why',
        widget=forms.Textarea,
        required=False,
        error_messages={
            'required': 'You must tell us why'})

    def __init__(self, *args, **kwargs):
        id = kwargs.pop('id')
        self.pk = id
        super().__init__(*args, **kwargs)
        self.field_list = [*self.fields]

    def clean_reasons_known_to_social_services_pith(self):
        if self.cleaned_data['known_to_social_services_pith'] == 'True' \
                and self.cleaned_data['reasons_known_to_social_services_pith'] ==  '':
            raise forms.ValidationError('You must tell us why')

        return self.cleaned_data['reasons_known_to_social_services_pith']
