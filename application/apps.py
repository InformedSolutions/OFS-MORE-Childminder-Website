"""
Initializing this app parameters

WARNING: BE CAREFULL WITH MODELS IN HERE. THIS MIGHT AFFECT PROD DATABASE
EVEN WHEN YOU'LL RUN TESTS! PLEASE READ DOCUMENTATION CAREFULLY BEFORE CHANGING ANYTHING IN HERE
"""
from django.apps import AppConfig

class ApplicationConfig(AppConfig):
    """General app configuration"""

    name = 'application'

    def register_signals_timelog(self):
        """
        Register timelog signals for certain models only
        """
        # Imports must stay here. If you put it outside of this class it will fail.
        # Because this app is loaded on when it reaches ready() method.
        # Any interaction with django will fail before this class
        from django.db.models.signals import post_init, post_save
        from application.signals import timelog_post_init, timelog_post_save

        timelog_models_instances = [self.get_model(model) for model in [\
            'ApplicantName',
            'ApplicantPersonalDetails',
            'ApplicantHomeAddress',
            'AdultInHome',
            'ChildInHome',
            'ChildcareType',
            'CriminalRecordCheck',
            'EYFS',
            'FirstAidTraining',
            'HealthDeclarationBooklet',
            'Reference',
            #'UserDetails',
        ]]

        for model in timelog_models_instances:
            post_init.connect(timelog_post_init, sender=model, dispatch_uid="timelog_post_init")
            post_save.connect(timelog_post_save, sender=model, dispatch_uid="timelog_post_save")

    def register_signals(self):
        """
        Register signals only for certains models
        """
        self.register_signals_timelog()

    def ready(self):

        self.register_signals()
