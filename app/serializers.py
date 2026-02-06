from rest_framework import serializers
from .models import AllVoter


class AllVoterSerializer(serializers.ModelSerializer):
    # Map JSON camelCase → model snake_case
    voterId = serializers.CharField(source="voter_id")
    fathersName = serializers.CharField(source="fathers_name")
    mothersName = serializers.CharField(source="mothers_name")
    sourceTitle = serializers.CharField(
        source="source_title",
        required=False,
        allow_null=True,
        allow_blank=True
    )

    class Meta:
        model = AllVoter
        # ⛔ id is NOT included
        fields = [
            "serial",
            "name",
            "voterId",
            "fathersName",
            "mothersName",
            "occupation",
            "dob",
            "address",
            "sourceTitle",
        ]
