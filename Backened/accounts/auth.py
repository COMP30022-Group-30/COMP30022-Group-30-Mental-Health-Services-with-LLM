from __future__ import annotations

from typing import Optional

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailUsernameBackend(ModelBackend):
    """
    Authentication backend that accepts either username or email as the principal.
    """

    def authenticate(
        self,
        request,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs,
    ):
        if username is None:
            username = kwargs.get("email")
        if username is None or password is None:
            return None

        UserModel = get_user_model()
        try:
            user = (
                UserModel.objects.filter(
                    Q(username__iexact=username) | Q(email__iexact=username)
                )
                .distinct()
                .get()
            )
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
