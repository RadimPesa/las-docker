# las-docker
Docker for LAS 1.0

## Obtain a copy
* Download a local copy of the Docker container source files:

```bash
git clone https://github.com/lasircc/las-docker.git
```

* Download the seed databases. Due their large size, the seed databases are stored separately from the GitHub repo on an FTP server. Please contact us at *las at ircc dot it* to get access credentials.

## Configuration

Edit the .env file in the root folder. In particular, set the following variables as appropriate
```HOST= *the name under which the LAS instance will be accessible*
EMAIL_HOST= *email server e.g. smtp.mail.com*
EMAIL_ADMIN_USER= *email user e.g. user@mycompany.com*
EMAIL_ADMIN_PASSWORD= *...*
EMAIL_PORT= *...*
EMAIL_USE_TLS= *True | False*
```
The other variables need not be changed unless you have any particular reason to use different values than the default ones.
