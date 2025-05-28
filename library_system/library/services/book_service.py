from django.contrib.contenttypes.models import ContentType
from django.db.models import OuterRef, Subquery
from library.models import Action, Book, UserAction


def get_borrowed_books_by_user(user_id):
    book_type = ContentType.objects.get_for_model(Book)

    latest_action_qs = UserAction.objects.filter(
        user_id=user_id, content_type=book_type, object_id=OuterRef("object_id")
    ).order_by("-timestamp")

    latest_action = latest_action_qs.values("action_type")[:1]

    borrowed_books = (
        UserAction.objects.filter(user_id=user_id, content_type=book_type)
        .values("object_id")  # group by book
        .annotate(latest_action_type=Subquery(latest_action))
        .filter(latest_action_type=Action.BORROW)
        .values_list("object_id", flat=True)
    )

    return Book.objects.filter(id__in=borrowed_books)
