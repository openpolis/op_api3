This procedure describes how to install a development environment on your laptop (or desktop) PC.

Get the development branch from github::

    git clone git@github.com:openpolis/op_api3.git op-api3
    

Create a virtualenv, the project is tested under python 2.7::

    mkvirtualenv op-api3


Install development requirements::

    pip install -r requirements/dev.txt
    

Downgrade ``sqlparse``, as versions reater than 0.1, cause bugs in django-debug-toolbar::

    pip remove sqlparse
    pip install sqlparse==0.1.19


Dump postgresql DB in production, and restore it in localhost.


In order to avoid dumping and restoring legacy mysql databases with open_politici and open_parlamento data, you can access the production databases through tunneling::

    ssh -L 3307:localhost:3306 -Nv root@api3.openpolis.it
    
    
Then, create or modify ``config/.env`` as follows, it is of paramount importance that ``127.0.0.1`` be used, instead of ``localhost`` in order for the tunneling into mysql to work::

    DEBUG=True
    DJANGO_SETTINGS_MODULE=api.settings.local
    SECRET_KEY=d5!5k+yk(+m3bi-d8htob2n-8064c)-wzh=n8u1pe@him!fx6v
    DB_DEFAULT_URL=postgis://postgres:@localhost/op_api3
    DB_POLITICI_URL=mysql://root:@127.0.0.1:3307/op_openpolis
    DB_PARLAMENTO16_URL=mysql://root:@127.0.0.1:3307/op_openparlamento
    DB_PARLAMENTO17_URL=mysql://root:@127.0.0.1:3307/opp17

    OPEN_COESIONE_DB_CONN_STRING=host='localhost' dbname='open_coesione' user='guglielmo' password=''
    OP_API_URI=http://localhost:8003
    OP_API_USERNAME=op
    OP_API_PASSWORD=op

    MAPIT_AREA_SRID=32632
    MAPIT_COUNTRY=GB
    MAPIT_RATE_LIMIT=[]

    POSTGIS_VERSION=(2,1,8)


Execute the ``runserver`` management command::

    python api_project/manage.py runserver
    
    
Connect to http://localhost:8000

