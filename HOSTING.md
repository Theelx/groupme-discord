## Pre-requirements
Assuming you have already complete the sections of the README up to but not including Configuration, your next steps are to configure Apache and Flask to run.

The following steps are intended for a VPS running Ubuntu 20.04, however Ubuntu 16.04+ or really any Debian-based system that uses ``apt`` should work the same.

## Steps
1. Install Apache by running:
```bash
sudo apt update
sudo apt install apache2
```
2. Enable WSGI for Flask-Apache interop with
```bash
sudo apt-get install libapache2-mod-wsgi-py3
sudo a2enmod wsgi
```
3. Replace the Server IP and the path to your copy of this repo in flask.conf.sample
4. Copy flask.conf.sample to /etc/apache2/sites-available and name it ``flask.conf``
5. Assuming you kept the name of the file as ``flask.conf`` and don't want a custom service name:
```bash
sudo a2ensite flask
```
6. Run the following (a reload might work too but a restart always works in my experience and seldom leads to more than 2-3s of downtime):
```bash
service apache2 restart
```

## Conclusion
Nice, now the flask/apache stuff should be set up! Go back to the README to continue with Configuration. If anything in this produced an error, feel free to file an issue, and I'll respond ASAP!