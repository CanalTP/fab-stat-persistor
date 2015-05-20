Fabric
======

This file must be executed via python fabric, you can list all *tasks* by:

    fab --list

The configuration is done by calling a first configuration task which set all the needed parameters in the fabric's ```env``` variable.

If your configuration is outside of this repository (and it should!), you can add it in the python path and call the ```use``` task with the task you want to import.

ex:
    ```PYTHONPATH=../stat-persistor-deployment-conf fab use:dev deploy```

if you want to give extra parameters to the configuration task, add them after it's name:

    ```PYTHONPATH=../stat-persistor-deployment-conf fab use:dev let:branch=release deploy```

Features:

* deploy/upgrade:

    ```fab <conf> deploy```

