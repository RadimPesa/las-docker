# las-docker
Docker for LAS 1.0
## Requirements
* Docker v.17.12.0-ce or newer
* docker-compose v.1.18.0 or newer

## Obtain a copy
* Download a local copy of the Docker container source files:

```bash
git clone https://github.com/lasircc/las-docker.git
```

* Download the seed databases. Due their large size, the seed databases are stored separately from the GitHub repo on an FTP server. Please contact us at *las at ircc dot it* to get access credentials. Extract the contents of the downloaded gzipped tarballs to the following paths:
- ```docker-entrypoint-initdb.d.tar.gz``` inside ```./las-docker/mysql/docker-entrypoint-initdb.d/```
- ```graph.db.tar.gz``` inside ```./las-docker/neo4j-data/graph.db```
- ```seq.tar.gz``` inside ```./las-docker/blat/seq/```

## Configuration
### Environment variables
Edit the ```.env``` file in the root folder. In particular, set the following variables as appropriate:
* ```HOST```: the name under which the LAS instance will be accessible
* ```EMAIL_HOST```: email server e.g. smtp.mail.com
* ```EMAIL_ADMIN_USER```: email user e.g. user@mycompany.com
* ```EMAIL_ADMIN_PASSWORD```
* ```EMAIL_PORT```
* ```EMAIL_USE_TLS```: *True* or *False*

The other variables need not be changed unless you have any particular reason to use different values than the default ones.

### SSL certificates
A self-signed certificate is provided with the bundle but will raise a security exception with most browsers. You may use your own certificate/key pair by overwriting the following files:
* ```./las-docker/web/ssl/apache.crt```: certificate file
* ```./las-docker/web/ssl/apache.key```: private key file

## Installation
Cd to the ```las-docker``` folder and issue the following command:
```bash
docker-compose build
```
The build process may take a long time (30 minutes or more), depending on your connection and CPU speed.

## Running the platform
Cd to the ```las-docker``` folder and issue the following command:
```bash
docker-compose run
```
On the first execution, genomic annotation data will be automatically downloaded from the web and imported inside the LAS instance database. This process may take a long time.
