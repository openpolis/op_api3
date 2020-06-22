Openpolis generic API, version 3, using django-rest-framework.

Complete re-design of the ``openpolitici`` database, splitted into ``pops`` and ``places`` sub-applications.

Import scripts to get data from the old openpolis database implemented.


To install in a development environment and start developing, without dumping
 the legacy databases::

    ssh -L 3307:localhost:3306 -Nv root@api3.openpolis.it

You need to have secure access to the api3.openpolis.it server.

Then these values can be set in the `.env` file::

    DB_DEFAULT_URL=postgis://postgres:@localhost/op_api3
    DB_POLITICI_URL=mysql://root:@127.0.0.1:3307/op_openpolis
    DB_PARLAMENTO16_URL=mysql://root:@127.0.0.1:3307/op_openparlamento
    DB_PARLAMENTO17_URL=mysql://root:@127.0.0.1:3307/opp17
    DB_PARLAMENTO18_URL=mysql://root:@127.0.0.1:3307/opp18

