from django.contrib.auth.hashers import PBKDF2PasswordHasher


class GroupPasswordHasher(PBKDF2PasswordHasher):
    """Lighter PBKDF2 for shared contest group passwords.

    Many teams log in at the same moment when the contest starts; the default
    1.2M iterations cost ~1-2s of CPU per login and stalls the whole server.
    Staff accounts keep the strong default hasher.
    """

    algorithm = "pbkdf2_sha256_group"
    iterations = 60_000
