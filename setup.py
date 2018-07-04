from setuptools import setup

setup(
    name='total_tolles_ferleihsystem',
    packages=['total_tolles_ferleihsystem'],
    include_package_data=True,
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
