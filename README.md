# ProductionGraph

Development Startup Procedure:

```bash
// initial start up

$ pip3 install --user --requirement requirements.txt
$ python3 manage.py tailwind install


// general start up

$ python3 manage.py tailwind start
$ python3 manage.py runserver
```

`tailwind start` command watches for changes to recompile css during development, so should be run concurrently with runserver command.
