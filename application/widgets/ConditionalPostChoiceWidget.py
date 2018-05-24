from govuk_forms.widgets import ChoiceWidget, RadioSelect


class ConditionalPostChoiceWidget(ChoiceWidget):
    template_name = 'widgets/multiple-select-post-conditional.html'
    option_template_name = 'widgets/multiple-select-option-post-conditional.html'


class ConditionalPostInlineRadioSelect(ConditionalPostChoiceWidget, RadioSelect):
    field_group_classes = 'inline'
    pass
