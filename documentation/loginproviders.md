# Login Providers

> The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119).

The TTF does not provide any special ui for user management.
It is intended to get the user management from external sources.
The system allows the use of multiple different external login sources via the `LOGIN_PROVIDERS` setting.
See [configuration.md](configuration.md) for the documentation on how to configure the system.

The `LOGIN_PROVIDERS` setting is a string array.
The names of the login providers can be added to this array.
Every login provider must only be added once.
