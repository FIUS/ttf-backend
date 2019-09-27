from setuptools import setup

__version__ = ''

setup(
    name='total_tolles_ferleihsystem',
    version=__version__,
    packages=['total_tolles_ferleihsystem'],
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[
        'flask',
        'flask_sqlalchemy',
        'flask_webpack',
        'flask_jwt_extended',
        'flask_bcrypt',
        'flask_cors',
        'celery',
        'ldap3',
    ],
)
