This procedure describes how to install a development environment,
using Vagrant + Ansible, on your laptop (or desktop) PC.

Prerequisites
=============

As a prerequisite, you need to have ansible installed as a global package,
and correctly configured on your machine, in order to locate the
depp-ansible roles.

.. code::

    # clone depp-ansible repository from gitlab
    pushd ~/Workspace
    git clone ssh://git@gitlab.equi.openpolis.it:9822/eraclitux/ansible.git depp-ansible

    # configure ansible, to use depp-ansible repository
    cat > ~/.ansible.cfg < EOF
    [defaults]
    roles_path = ~/Workspace/depp-ansible/playbooks/roles
    nocows = 1
    remote_user = vagrant
    private_key_file = ~/.vagrant.d/insecure_private_key
    host_key_checking = False
    EOF


Code download
=============

Download source code, from github to your host.

.. code::
    cd ~/workspace/op-api3
    git clone https://github.com/openpolis/op_api3/ op-api3
    

VM Installation
===============

A vagrant machine is launched and provisioned with all OS packages and
python packages needed to properly run the django app and all needed services
in the virtual machines, leaving the app source code in the host.

.. code::

    cd ~/workspace/op-api3/config
    vagrant up


Data transfer
#############





Now, open http://192.168.111.104:8000 in your browser!



   

VM Operations
=============

This describes how to have the prepared environment start and begin work.

.. code::

    cd deploy-config
    vagrant up
    vagrant ssh -c "source virtualenvs/op-api3/bin/activate; cd /vagrant/op-api4; python api_project/manage.py runserver 0.0.0.0:8000"


Now, open http://192.168.111.104:8000 in your browser,
start modifying code and see the changes in the browser.

(Debugging in pycharm has yet to be configured correctly)

Libraries and packages updates can be checked (optionally) with:

.. code::

    vagrant provision
