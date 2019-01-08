from authentication.google import GoogleAuth

providers = {
    'google': GoogleAuth
}


def login(provider, *args, **kwargs):
    providers.get(provider)().login(*args, **kwargs)
