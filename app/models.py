from django.db import models
from django.utils.translation import gettext_lazy as _


def _collections_directory_path(instance, filename):
    return '/'.join(['collections', filename])


class Collection(models.Model):
    collected_at = models.DateTimeField(_("Collection Time"), auto_now_add=True)
    filename = models.CharField(_("Filename"), max_length=128, db_index=True)
    file = models.FileField(upload_to=_collections_directory_path)

    def __str__(self):
        return self.filename

    class Meta:
        ordering = ["-collected_at"]
