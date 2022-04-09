from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model


def run(*args):
    if settings.INITIAL_ADMIN_USER and settings.INITIAL_ADMIN_EMAIL and settings.INITIAL_ADMIN_PASSWORD:
        django_admin_user = settings.INITIAL_ADMIN_USER
        django_admin_email = settings.INITIAL_ADMIN_EMAIL
        django_admin_password = settings.INITIAL_ADMIN_PASSWORD
    elif len(args) == 3:
        django_admin_user = args[0]
        django_admin_email = args[1]
        django_admin_password = args[2]
    else:
        print("Missing arguments.  Example usage:")
        print("./manage.py runscript create_super_user --script-args <admin user> <admin email> <admin password>")
        exit(1)
    MyUser = get_user_model()
    MyUser.objects.filter(username__exact=django_admin_user).count() == 0 or exit(1)
    new_super_user = MyUser(username=django_admin_user, email=django_admin_email, is_superuser=True, is_staff=True)
    new_super_user.password = make_password(django_admin_password)
    new_super_user.save()
    MyUser.objects.filter(username__exact=django_admin_user).count() == 1 or exit(1)
