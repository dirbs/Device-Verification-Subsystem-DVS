## Device Verification System (DVS)
Device Verification System (DVS) that is part of the Device Identification,
Registration and Blocking (DIRBS) system.

### Deployment
1. Install and configure [Python 3.6](https://www.python.org)
2. Install and configure [Python PIP](https://pip.pypa.io/en/stable/installing/)
3. Make a new virtual environment
```bash
$ pip install virtualenv
```

4. Create a new virtual environment for the project
```bash
$ virtualenv venv
```

5. Activate the virtual environment
```bash
$ source venv/bin/activate
```

6. Install the project requirements
```bash
$ pip install -r requirements.txt
```

7. Build the packages
```bash
$ python setup.py build
```

8. Install the packages in venv
```bash
$ python setup.py install
```

9. Install rabbitmq-server
```bash
$ sudo apt-get install rabbitmq-server
```
9. Start celery worker
```bash
$ celery -A app.celery worker --concurrency=10 --loglevel=info
```

### Usage
#### Running Tests
Run test-suits:
```bash
$ python -m unittest tests/main.py
```

### Contribution

### Licensing

### References
- [Python 3.6](https://www.python.org/)
- [PyCharm Community](https://www.jetbrains.com/pycharm/)
- [Postgres](https://www.postgresql.org/)
