"""
File for models of the app core.
"""
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """
    Base model for all models.

    This class provides common fields and methods for all models in the Django project.
    It includes fields such as 'created_at', 'updated_at', 'deleted_at', and 'is_active',
    and methods for saving and updating instances of the model.

    Fields:
    - created_at: A DateTimeField that automatically sets the value to the current date
                    and time when an instance is created.
    - updated_at: A DateTimeField that automatically updates the value to the current date and
                    time when an instance is updated.
    - deleted_at: A DateTimeField that stores the date and time when an instance is deleted.
                    If the instance is not deleted, the value is set to None.
    - is_active: A BooleanField that indicates whether an instance is active or not.
                    If an instance is not active, it is considered deleted and the 'deleted_at' field is set.

    Methods:
    - save(): Overrides the default save method to set the 'deleted_at' field if the instance is not active.
    - update(): A custom method that calls the save method to update an instance of the model.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    is_active = models.BooleanField(default=True)

    class Meta:
        """
        Meta class for BaseModel

        Abstract is True because this model is not a table in the database, is a base for other models.
        """

        abstract = True

    def save(self, *args, **kwargs):
        """
        Overrides the default save method.

        If the instance is active, sets the 'deleted_at' field to None and saves the instance.
        If the instance is not active, sets the 'deleted_at' field to the current date and time and saves the instance.
        """
        if self.is_active:
            self.deleted_at = None
            super().save(*args, **kwargs)
        else:
            self.deleted_at = timezone.now()
            super().save(*args, **kwargs)

    def update(self, *args, **kwargs):
        """
        Updates an instance of the model.

        If the instance is active, sets the 'deleted_at' field to None and calls the save method.
        If the instance is not active, sets the 'deleted_at' field to the current date and time and calls save method.
        """
        if self.is_active:
            self.deleted_at = None
            self.save(*args, **kwargs)
        else:
            self.deleted_at = timezone.now()
            self.save(*args, **kwargs)
