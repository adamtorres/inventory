from config import settings


def collect_settings():
    return {
        "BASE_DIR": settings.BASE_DIR,
        "DEBUG": settings.DEBUG,
        "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
        "INSTALLED_APPS": [ia for ia in settings.INSTALLED_APPS if not ia.startswith("django")],
        "MIDDLEWARE": [mw for mw in settings.MIDDLEWARE if not mw.startswith("django")],
        "TEMPLATES.DIRS": [t["DIRS"] for t in settings.TEMPLATES],
        "STATIC_ROOT": settings.STATIC_ROOT,
        "STATICFILES_DIRS": settings.STATICFILES_DIRS,
        "DATABASES.default": {
            k: v for k, v in settings.DATABASES["default"].items()
            if k in ['NAME', 'USER', 'PASSWORD', 'HOST', 'PORT', 'TIME_ZONE']}
    }


def run():
    print("")
    for setting, value in collect_settings().items():
        print(f"{setting:>20} = {value!r}")
