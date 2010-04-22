# Copyright 2007-2009, Red Hat, Inc
# Steve 'Ashcrow' Milner <smilner@redhat.com>
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
LDAP Backend with white listed user list.
"""

try:
    import ldap
except ImportError:
    # no ldap support
    pass


from django.http import HttpResponseRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.views import login
from django.conf import settings


class LDAPBackend(object):
    """
    The LDAP backend for authentication.
    """

    def authenticate(self, username=None, password=None):
        """
        In charge of deciding if the user is authorized.

        @param self: Internal LDAPBackend object.
        @type self: LDAPBackend

        @param username: Username to auth.
        @type username: str

        @param password: Password to auth with.
        @type password: str
        """
        if username and password:
            lcon = ldap.open(settings.LDAP_SERVER)
            try:
                lcon.protocol_version = ldap.VERSION3
                lcon.start_tls_s()
                lcon.simple_bind_s(settings.LDAP_USER_BASE % username,
                                   password)
                return self.auth_or_make_user(username, password)
            except:
                return None
        else:
            return None

    def auth_or_make_user(self, username=None, password=None):
        """
        In charge of deciding if the user is authorized.

        @param self: Internal LDAPBackend object.
        @type self: LDAPBackend

        @param username: Username to auth.
        @type username: str

        @param password: Password to auth with.
        @type password: str

        @return: User object
        @rtype: User
        """
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username)
            user.set_password(password)

            user.is_staff = False
            user.is_superuser = False
            user.save()
        return user

    def get_user(self, user_id):
        """
        Returns a user object.

        @param self: Internal LDAPBackend object.
        @type self: LDAPBackend

        @param user_id: The id of the user to get.
        @type user_id: int

        @return: User object
        @rtype: User
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class RemoteUserBackend(ModelBackend):
    """
    This backend is to be used in conjunction with the ``RemoteUserMiddleware``
    found in the middleware module of this package, and is used when the server
    is handling authentication outside of Django.

    By default, the ``authenticate`` method creates ``User`` objects for
    usernames that don't already exist in the database.  Subclasses can disable
    this behavior by setting the ``create_unknown_user`` attribute to
    ``False``.
    """

    # Create a User object if not already in the database?
    create_unknown_user = False

    def authenticate(self, remote_user):
        """
        The username passed as ``remote_user`` is considered trusted.  This
        method simply returns the ``User`` object with the given username,
        creating a new ``User`` object if ``create_unknown_user`` is ``True``.

        Returns None if ``create_unknown_user`` is ``False`` and a ``User``
        object with the given username is not found in the database.
        """
        if not remote_user:
            return
        user = None
        username = self.clean_username(remote_user)

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if self.create_unknown_user:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user = self.configure_user(user)
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass
        return user

    def clean_username(self, username):
        """
        Performs any cleaning on the "username" prior to using it to get or
        create the user object.  Returns the cleaned username.

        By default, returns the username unchanged.
        """
        return username

    def configure_user(self, user):
        """
        Configures a user after creation and returns the updated user.

        By default, returns the user unmodified.
        """
        return user


def smart_login(request,
                template_name='registration/login.html',
                redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Checks for existing auth and redirects if found.
    Otherwise call login view.
    """
    if request.user and request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    return login(request,
                 template_name='registration/login.html',
                 redirect_field_name=redirect_field_name)
