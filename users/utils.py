from uuid import uuid4

from django.contrib.auth import login
from django.contrib.auth.models import User

from users.tasks import send_custom_user_email


def create_user_for_anonymous_checkout(request, customer):
    """
    This function creates a user if he is not authenticated
    :param request:
    :param customer:
    :return:
    """
    try:
        email = request.POST.get('email')
        password = str(uuid4()).replace("-", "")[:10]
        username = email.split("@")[0] + password
        # checking if the email exists
        if User.objects.filter(email=email).exists():
            return False
        # verifying if the email has been used and if it has been used i regenerate a new one by adding it to the
        # order
        if User.objects.filter(username=username).exists():
            username = username + str(uuid4()).replace("-", "")[:5]
        user = User.objects.create(email=email, username=username)
        user.set_password(password)
        user.save()
        #  if user exist
        if user is not None:
            #  login the user with our backend authentication
            login(request, user, backend="allauth.account.auth_backends.AuthenticationBackend")
            print("the request user now oooo", request.user)
            #  check if the user is now authenticated
            if request.user.is_authenticated:
                send_custom_user_email(email=email, password=password, first_name=customer.first_name,
                                       last_name=customer.last_name)
                return True
    except Exception as e:
        print(e)
        return False
