from django.shortcuts import redirect


def email_verified_required(view_func):
    def wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('account:login')

        if not request.user.is_email_verified:
            return redirect("account:verify_email")
        return view_func(request, *args, **kwargs)
    return wrapped_view


class EmailVerifiedRequiredMixin:
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return email_verified_required(view)