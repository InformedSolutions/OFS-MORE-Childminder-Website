import collections
from django import forms
from govuk_forms.widgets import NumberInput

from application.forms import ChildminderForms, childminder_dbs_duplicates_household_member_check
from application.models import Application


class PITHDeclarationForm(ChildminderForms):
    """
    GOV.UK form for the People in the Home: Declaration check box.
    """
    