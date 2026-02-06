from django.contrib import admin
from .models import AllVoter


@admin.register(AllVoter)
class AllVoterAdmin(admin.ModelAdmin):
    # Columns shown in list view
    list_display = (
        "serial",
        "name",
        "voter_id",
        "fathers_name",
        "mothers_name",
        "occupation",
    )

    # Make name & voter_id clickable
    list_display_links = ("serial", "name")

    # Fast search (very important for voter data)
    search_fields = (
        "serial",
        "name",
        "voter_id",
        "fathers_name",
        "mothers_name",
        "address",
    )

    # Right sidebar filters
    list_filter = (
        "occupation",
        "created_at",
    )

    # Pagination (important for performance)
    list_per_page = 50

    # Default ordering
    ordering = ("serial",)

    # Read-only system fields
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    # Group fields for clean admin UI
    fieldsets = (
        ("ভোটারের তথ্য", {
            "fields": (
                "serial",
                "name",
                "voter_id",
                "dob",
                "occupation",
            )
        }),
        ("পারিবারিক তথ্য", {
            "fields": (
                "fathers_name",
                "mothers_name",
            )
        }),
        ("ঠিকানা ও উৎস", {
            "fields": (
                "address",
                "source_title",
            )
        }),
        ("সিস্টেম তথ্য", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )
