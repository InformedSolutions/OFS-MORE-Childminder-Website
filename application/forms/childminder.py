from django import forms
from govuk_forms.forms import GOVUKForm

from ..models import ArcComments


class ChildminderForms(GOVUKForm):
    """
    Parent class of all later forms.
    Contains methods for checking the existence, and the removing, of flags from the ARC user.
    """

    pk = ''
    field_list = []

    def check_flag(self):
        """
        For a class to call this method it must set self.pk and self.field_list.  This method simply checks whether
        or not a field is flagged, and raises a validation error if it is
        :return: Form validation error.
        """
        for i in self.field_list:
            if ArcComments.objects.filter(table_pk=self.pk, field_name=i).exists():
                log = ArcComments.objects.get(table_pk=self.pk, field_name=i)
                try:
                    if log.flagged:
                        raise forms.ValidationError(log.comment)
                    else:
                        forms.ValidationError('')
                except Exception as ex:
                    self.cleaned_data = ''
                    self.add_error(i, ex)
            self.if_name(i, True)
            self.if_address(i, True)

    def remove_flag(self):
        """
        This method is called when a form is posted.  It simply removes the validation errors triggered by the Arc
        comments.
        :return: Update the arc comments to remove the flag (but keep the comment)
        """
        log = ''
        for i in self.field_list:
            if ArcComments.objects.filter(table_pk=self.pk, field_name=i).count() == 1:
                log = ArcComments.objects.get(table_pk=self.pk, field_name=i)
                log.flagged = False
                log.save()
            self.if_name(i, False)
            self.if_address(i, False)

    def if_name(self, field, enabled):
        """
        This checks if a name has been flagged, as first, middle or last cannot be flagged individually.
        :param field:
        :return:
        """

        log = None
        if ArcComments.objects.filter(
                table_pk=self.pk).count() > 0 and field == 'first_name' or 'last_name' or 'middle_names':

            if ArcComments.objects.filter(table_pk=self.pk, field_name='name').exists():
                log = ArcComments.objects.get(table_pk=self.pk, field_name='name')

            if ArcComments.objects.filter(table_pk=self.pk, field_name='full_name').exists():
                log = ArcComments.objects.get(table_pk=self.pk, field_name='full_name')
            try:
                if hasattr(log, 'comment'):

                    if log.flagged:
                        if enabled:
                            raise forms.ValidationError(log.comment)
                        else:
                            print("DISABLE FLAG")
                            log.flagged = False
                            log.save()
                else:
                    forms.ValidationError('')

            except Exception as ex:

                self.cleaned_data = ''
                if field == 'first_name':
                    self.add_error(field, ex)

                else:
                    self.add_error(field, '')

    def if_address(self, field, enabled):
        """
        This checks if an address has been flagged, as each address field cannot be flagged individually.
        :param field:
        :return:
        """

        log = None
        # Right now only an address as a whole can be flagged, and the message is repeated for each field
        if ArcComments.objects.filter(table_pk=self.pk).count() > 0:
            if field == 'street_line1' or 'street_line2' or 'town' or 'county' or 'country' or 'postcode':

                if ArcComments.objects.filter(table_pk=self.pk, field_name='address').exists():
                    log = ArcComments.objects.get(table_pk=self.pk, field_name='address')

                if ArcComments.objects.filter(table_pk=self.pk, field_name='home_address').exists():
                    log = ArcComments.objects.get(table_pk=self.pk, field_name='home_address')
                try:

                    if hasattr(log, 'comment'):
                        if log.flagged:
                            if enabled:
                                raise forms.ValidationError(log.comment)
                            else:
                                print("DISABLE FLAG")
                                log.flagged = False
                                log.save()
                    else:
                        forms.ValidationError('')
                except Exception as ex:
                    self.cleaned_data = ''
                    if field == 'street_name_and_number':
                        self.add_error(field, ex)
                    else:
                        self.add_error(field, '')
