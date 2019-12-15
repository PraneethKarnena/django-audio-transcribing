from django.db import models


class AudioDataModel(models.Model):
    uploaded_file = models.FileField(null=False, blank=False)
    exported_file_name = models.TextField(null=True, blank=True)

    transcript = models.TextField(null=True, blank=True)

    error_occurred = models.BooleanField(default=False, null=False, blank=False)
    error_message = models.TextField(null=True, blank=True)

    STATUS_CHOICES = (
        ('PEN', 'Pending'),
        ('COM', 'Complete'),
        ('ERR', 'Error'),
    )
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, null=False, blank=False, default='PEN')

    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.uploaded_file} - {self.created_at}'