from django.contrib.contenttypes.models import ContentType
from library.models import Action, Author, Book, UserAction
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["full_name"]

    permission_classes = [IsAuthenticated]


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)
    is_borrowed = serializers.SerializerMethodField()
    is_borrowed_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "summary",
            "isbn_10",
            "authors",
            "is_borrowed",
            "is_borrowed_by_user",
        ]

    permission_classes = [IsAuthenticated]

    def get_is_borrowed(self, obj) -> bool:
        """Check if the book is borrowed at the moment.

        Returns:
            bool: True if book is borrowed, False if available.
        """
        book_ct = ContentType.objects.get_for_model(Book)

        borrow_count = UserAction.objects.filter(
            action_type=Action.BORROW, content_type=book_ct, object_id=obj.id
        ).count()

        return_count = UserAction.objects.filter(
            action_type=Action.RETURN, content_type=book_ct, object_id=obj.id
        ).count()

        return borrow_count > return_count

    def get_is_borrowed_by_user(self, obj) -> bool:
        """Check if the book is borrowed by the specific user.

        Returns:
            bool: True if book is borrowed, False if available.
        """
        user = self.context["request"].user
        if not user or not user.is_authenticated:
            return False

        book_ct = ContentType.objects.get_for_model(Book)

        borrow_count = UserAction.objects.filter(
            user=user, action_type=Action.BORROW, content_type=book_ct, object_id=obj.id
        ).count()

        return_count = UserAction.objects.filter(
            user=user, action_type=Action.RETURN, content_type=book_ct, object_id=obj.id
        ).count()

        return borrow_count > return_count


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
