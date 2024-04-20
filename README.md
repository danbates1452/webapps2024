# PalPay (webapps2024)

'PalPay': a web-based, multi-user payment service using the Django framework. Written for 944G5: Web Applications and Services at the University of Sussex in 2024.

### Install required packages
With Python 3.8, and your virtual environment active:
```commandline
pip install -r ./requirements.txt
```

### Run Locally
```commandline
python3 ./manage.py runserver_plus localhost:8000 --cert-file webapps.crt --key-file webapps_decrypted.key
```

