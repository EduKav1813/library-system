from django.contrib.contenttypes.models import ContentType
from library.models import Author, Book, UserAction
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["full_name"]

    permission_classes = [IsAuthenticated]


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)

    class Meta:
        model = Book
        fields = ["title", "summary", "isbn_10", "authors"]

    permission_classes = [IsAuthenticated]


class UserActionSerializer(serializers.ModelSerializer):
    target_type = serializers.CharField(write_only=True)
    target_id = serializers.IntegerField(write_only=True)
    target_repr = serializers.SerializerMethodField(read_only=True)
    string = serializers.SerializerMethodField()  # String representation of the action

    class Meta:
        model = UserAction
        fields = [
            "user",
            "action_type",
            "target_type",
            "target_id",
            "target_repr",
            "timestamp",
            "comment",
            "string",
        ]

    def get_string(self, obj):
        return str(obj)

    def create(self, validated_data):
        model_name = validated_data.pop("target_type")
        object_id = validated_data.pop("target_id")

        try:
            content_type = ContentType.objects.get(model=model_name)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError("Invalid target_type.")

        validated_data["content_type"] = content_type
        validated_data["object_id"] = object_id

        return super().create(validated_data)

    def get_target_repr(self, obj):
        return str(obj.target)  # or more detailed if needed
