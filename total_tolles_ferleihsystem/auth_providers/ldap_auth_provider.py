"""
Auth Providers which provides LDAP login
"""
from typing import List, Dict

from ldap3 import Connection, Server, AUTO_BIND_TLS_BEFORE_BIND, SUBTREE
from ldap3.core.exceptions import LDAPSocketOpenError, LDAPBindError

from ..login import LoginProvider
from .. import APP, AUTH_LOGGER

class LDAPAuthProvider(LoginProvider, provider_name="LDAP"):
    """
    Login Provider with connection to LDAP Server
    """

    ldap_uri: str #The URL of the ldpa server
    port: int #The port of the ldap server. Use None for default.
    ssl: bool #Whether to use ssl for the connection.
    start_tls: bool #Whether to upgrade connection with StartTLS once bound.
    user_search_base: str #The search base for users.
    group_search_base: str #The search base for groups.
    user_rdn: str #The RDN for users.
    user_uid_field: str # The field of a user, which is the name, that is i the group_membership_field
    group_membership_field: str #The field of a group, which contains the username
    moderator_filter: str #A moderator must match this filter
    admin_filter: str #A admininstrator must match this filter
    moderator_group_filter: str # A moderator must be in at least one of the matched groups
    admin_group_filter: str # A admin must be in at least one of the matched groups

    server: Server = None

    known_users: Dict[str, bool]

    def __init__(self):
        self.ldap_uri: str = APP.config["LDAP_URI"] #The URL of the ldpa server
        self.port: int = APP.config["LDAP_PORT"] #The port of the ldap server. Use None for default.
        self.ssl: bool = APP.config["LDAP_SSL"] #Whether to use ssl for the connection.
        self.start_tls: bool = APP.config["LDAP_START_TLS"] #Whether to upgrade connection with StartTLS once bound.
        self.user_search_base: str = APP.config["LDAP_USER_SEARCH_BASE"] #The search base for users.
        self.group_search_base: str = APP.config["LDAP_GROUP_SEARCH_BASE"]  #The search base for groups.
        self.user_rdn: str = APP.config["LDAP_USER_RDN"] #The RDN for users.
        self.user_uid_field: str = APP.config["LDAP_USER_UID_FIELD"] # The field of a user, which is the name, that is i the group_membership_field
        self.group_membership_field: str = APP.config["LDAP_GROUP_MEMBERSHIP_FIELD"] #The field of a group, which contains the username
        self.moderator_filter: str = APP.config["LDAP_MODERATOR_FILTER"] #A moderator must match this filter
        self.admin_filter: str = APP.config["LDAP_ADMIN_FILTER"] #A admininstrator must match this filter
        # A moderator must be in at least one of the matched groups
        self.moderator_group_filter: str = APP.config["LDAP_MODERATOR_GROUP_FILTER"]
        # A admin must be in at least one of the matched groups
        self.admin_group_filter: str = APP.config["LDAP_ADMIN_GROUP_FILTER"]

        self.server: Server = None
        self.known_users = {}

    def init(self) -> None:
        self.server = Server(self.ldap_uri, port=self.port, use_ssl=self.ssl)

    def valid_user(self, user_id: str) -> bool:
        return True

    @classmethod
    def combine_filters(cls, filters: List[str]) -> str:
        """
        Combines the given filters with a or
        """
        non_empty_filters = list(filter(None, filters))

        if not non_empty_filters:
            return ""
        elif len(non_empty_filters) == 1:
            return non_empty_filters.pop()
        else:
            return "(|" + ''.join(non_empty_filters) + ")"

    def valid_password(self, user_id: str, password: str) -> bool:
        try:
            user_str = self.user_rdn + "=" + user_id + "," + self.user_search_base
            with Connection(self.server,
                            user=user_str,
                            password=password,
                            auto_bind=AUTO_BIND_TLS_BEFORE_BIND,
                            read_only=True) as conn:

                user_base_filter = "(" + self.user_rdn + "=" + user_id + ")"
                user_filter = user_base_filter
                all_users_filter = self.combine_filters([self.moderator_filter, self.admin_filter])

                if all_users_filter:
                    user_filter = "(&" + all_users_filter + user_base_filter + ")"

                if not conn.search(self.user_search_base,
                                   user_filter,
                                   search_scope=SUBTREE,
                                   attributes=[self.user_uid_field]):
                    AUTH_LOGGER.info("User %s is not in the user filter", user_id)
                    return False

                user_uid = str(conn.entries.pop()[self.user_uid_field])

                group_base_filter = "(" + self.group_membership_field + "=" + user_uid + ")"
                group_filter = group_base_filter
                all_groups_filter = self.combine_filters([self.moderator_group_filter, self.admin_group_filter])

                if all_groups_filter:
                    group_filter = "(&" + all_groups_filter + group_base_filter + ")"

                if not conn.search(self.group_search_base, group_filter, search_scope=SUBTREE):
                    AUTH_LOGGER.info("User %s is not in any group of the group filter", user_id)
                    return False

                admin_user_filter = user_base_filter
                all_admin_users_filter = self.combine_filters([self.admin_filter])
                if all_admin_users_filter:
                    admin_user_filter = "(&" + all_admin_users_filter + user_base_filter + ")"

                admin_group_filter = group_base_filter
                all_admin_groups_filter = self.combine_filters([self.admin_group_filter])
                if all_admin_groups_filter:
                    admin_group_filter = "(&" + all_admin_groups_filter + group_base_filter + ")"

                in_admin_user_filter = conn.search(self.user_search_base,
                                                   admin_user_filter,
                                                   search_scope=SUBTREE)
                in_admin_group_filter =  conn.search(self.group_search_base,
                                                     admin_group_filter,
                                                     search_scope=SUBTREE)
                if (in_admin_user_filter and in_admin_group_filter):
                    self.known_users[user_id] = True
                else:
                    self.known_users[user_id] = False

                AUTH_LOGGER.debug("Valid login from user %s. User in admin user filter: %s. User in admin group: %s", user_id, str(in_admin_user_filter), str(in_admin_group_filter))

                return True

        except LDAPSocketOpenError as error:
            raise ConnectionError("Unable to connect to LDAP Server.") from error
        except LDAPBindError:
            return False
        return False

    def is_admin(self, user_id: str) -> bool:
        return self.known_users[user_id]

    def is_moderator(self, user_id: str) -> bool:
        return True
