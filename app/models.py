import uuid
from django.db import models


class Voter(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    serial = models.CharField(
        max_length=10,
        verbose_name="ক্রমিক নং"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="ভোটারের নাম"
    )
    voter_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="ভোটার আইডি"
    )
    fathers_name = models.CharField(
        max_length=255,
        verbose_name="পিতার নাম"
    )
    mothers_name = models.CharField(
        max_length=255,
        verbose_name="মাতার নাম"
    )
    occupation = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="পেশা"
    )
    dob = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="জন্ম তারিখ"
    )
    address = models.TextField(
        verbose_name="ঠিকানা"
    )
    source_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="তথ্যের উৎস"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Voter"
        verbose_name_plural = "Voters"
        ordering = ["serial"]

    def __str__(self):
        return f"{self.name} ({self.voter_id})"


from django.db import models


class AllVoter(models.Model):
    serial = models.CharField(
        max_length=10,
        verbose_name="ক্রমিক নং"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="ভোটারের নাম"
    )
    voter_id = models.CharField(
        max_length=20,
    
        verbose_name="ভোটার আইডি"
    )
    fathers_name = models.CharField(
        max_length=255,
        verbose_name="পিতার নাম"
    )
    mothers_name = models.CharField(
        max_length=255,
        verbose_name="মাতার নাম"
    )
    occupation = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="পেশা"
    )
    dob = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="জন্ম তারিখ"
    )
    address = models.TextField(
        verbose_name="ঠিকানা"
    )
    source_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="তথ্যের উৎস"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["serial"]

    def __str__(self):
        return f"{self.name} ({self.voter_id})"


