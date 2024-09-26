import json
import logging
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import login as django_login, get_user_model

# Initialize OAuth
oauth = OAuth()
oauth.register(
    'auth0',
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    server_metadata_url=f'https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'},
)

# Set up logger
logger = logging.getLogger(__name__)

def loginSSO(request):
    return oauth.auth0.authorize_redirect(request, redirect_uri=request.build_absolute_uri(reverse('callback')))

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    user_info = oauth.auth0.parse_id_token(request, token)

    email = user_info.get('email')
    User = get_user_model()

    # Get or create the user in the database
    user, created = User.objects.get_or_create(email=email, defaults={
        'first_name': user_info.get('given_name', ''),
        'last_name': user_info.get('family_name', ''),
    })

    # Log the user in
    django_login(request, user)

    if created:
        logger.info(f"New user registered: {email}")
    else:
        logger.info(f"User logged in: {email}")

    return redirect('index')  # Redirect to a success page or dashboard

def logout(request):
    request.session.clear()
    return redirect(f'https://{settings.AUTH0_DOMAIN}/v2/logout?returnTo={request.build_absolute_uri(reverse("index"))}&client_id={settings.AUTH0_CLIENT_ID}')

def index(request):
    return render(request, 'authapp/index.html', {
        'user_authenticated': request.user.is_authenticated,
    })
