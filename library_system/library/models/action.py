from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

User = get_user_model()


class Action(models.TextChoices):
    BORROW = "borrow", "Borrow"
    RETURN = "return", "Return"


class UserAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="actions")
    action_type = models.CharField(max_length=20, choices=Action.choices)

    # Generic relation to any model (Book, Author, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey("content_type", "object_id")

    # Optional extra fields
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} {self.action_type} {self.target}"
