# PalPay (webapps2024)

'PalPay': a web-based, multi-user payment service using the Django framework. Written for 944G5: Web Applications and Services at the University of Sussex in 2024, this project attained a mark of 88.5/100. A video walkthrough of its features can be found here: https://youtu.be/3OxfNwomvHg.

For information on what was implemented and how, database setup, security considerations, APIs, and AWS deployment, see the attached report.pdf.

### Install required packages
With Python 3.8, and your virtual environment active:
```commandline
pip install -r ./requirements.txt
```

### Run Locally
With HTTPS: (you will have to replace the certificate and key files)
```commandline
python3 ./manage.py runserver_plus localhost:8000 --cert-file webapps.crt --key-file webapps_decrypted.key
```
With HTTP:
```commandline
python3 ./manage.py runserver
```
