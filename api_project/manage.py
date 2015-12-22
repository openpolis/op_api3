#!/usr/bin/env python
import os
import sys
import environ

if __name__ == "__main__":
    root = environ.Path(__file__) - 2  # three folder back (/a/b/c/ - 3 = /)

    # set default values and casting
    env = environ.Env(
        DEBUG=(bool, True),
    )
    env.read_env(root('deploy_config/.env'))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", env('DJANGO_SETTINGS_MODULE'))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
