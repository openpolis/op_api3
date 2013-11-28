This is the old pops application and it is not used anymore.
It tried to map the same resources mapped in the new pops application,
but without following any standards.

Tables can be safely removed from the postgresql database, when upgrading to the new app.

Pops dows not have models, and uses popolo models, to start with.
So, once old ``pops`` tables are removed from the database,
``syncdb`` can be safely invoked to generate ``popolo`` tables.

These are the instructions to upgrade the database::

    psql -Uguglielmo op_api3
    # drop table pops_alternativename;
    # drop table pops_code;
    # drop table pops_contact;
    # drop table pops_contacttype;
    # drop table pops_personhaseducationlevel;
    # drop table pops_personhasprofession;
    # drop table pops_person;
    # drop table pops_educationlevel;
    # drop table pops_profession;

    python manage.py syncdb



