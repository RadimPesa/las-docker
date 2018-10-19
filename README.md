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

* Download the seed databases. Due their large size, the seed databases are stored separately from the GitHub repo on an FTP server. Please contact us at *las* at *ircc* dot *it* to get access credentials. Extract the contents of the downloaded gzipped tarballs to the following paths:
    * ```docker-entrypoint-initdb.d.tar.gz``` inside ```./las-docker/mysql/docker-entrypoint-initdb.d/```
    * ```graph.db.tar.gz``` inside ```./las-docker/neo4j-data/graph.db/```
    * ```seq.tar.gz``` inside ```./las-docker/blat/seq/```

**REMARK:** Please download the scripts from the DB_updates folder to update the database after the installation. Each script contains the date of the last update. If you are installing after that date you do not need to run the scripts. Differently, open phpmyadmin at http://`<your-domain>`:8082 and run the scripts ordered by date.

## Configuration
### Environment variables
Edit the ```.env``` file in the root folder. In particular, set the following variables as appropriate:
* ```ADMIN_PASSWORD```: password (of your choice) for the LAS administrator user
* ```HOST```: host name under which the LAS instance will be accessible e.g. las.mycompany.com
* ```EMAIL_HOST```: email server e.g. smtp.mail.com
* ```EMAIL_ADMIN_USER```: email user e.g. user@mycompany.com
* ```EMAIL_ADMIN_PASSWORD```
* ```EMAIL_PORT```
* ```EMAIL_USE_TLS```: *True* or *False*
* ```DEFAULT_FROM_EMAIL```: email address used in From message header

Make sure you choose a strong password for the administrator user and keep it private, since inadvertent access to this account may compromise the data in the LAS system.
The other variables need not be changed unless you have a specific reason (and know what you're doing).

<!--
### ServerName Apache
Edit the fqdn.conf file in /web/conf folder to define your domain.
-->

### SSL certificates
A self-signed certificate is provided with the bundle but will raise a security exception with most browsers. You may use your own certificate/key pair by overwriting the following files:
* ```./las-docker/web/ssl/apache.crt```: certificate file
* ```./las-docker/web/ssl/apache.key```: private key file

## Installation and deployment
Cd to the ```las-docker``` folder and issue the following command:
```bash
docker-compose build
docker-compose up
```
The build process may take a long time (30 minutes or more), depending on your connection and CPU speed.
Next, upon the first execution, seed databases will be automatically imported, which will also take some time (10 minutes or more).

## Starting/stopping the platform
The platform may be stopped and restarted using the following commands:
```bash
docker-compose stop
```
and
```bash
docker-compose start
```
To stop and completely remove all containers, issue the following command:
```bash
docker-compose down
```

---
# Running scripts for genomic annotation management

The Genomic Annotation Manager module exploits annotation data from various public resources. These data must be downloaded and imported in the database prior to using the module. If you don't plan to use the Genomic Annotation Module, you can safely ignore this step (or you can always run it at a later time).
We provide a script that automatically handles the download and import process. To start the script, run the code below in a terminal:
```bash
docker-compose run web /srv/www/newAnnotationsManager/scripts/populate_tables_2.sh
```
It will take a long time (from a few hours to a whole day), so sit back an relax. ;)

# Running scripts for clinical data management

> _Hello there!_

Today's LAS is a huge modular project and has been changing over time. The designs of the modules reflect such an evolution of the system. We will work in the next future to a _normalization_ of the modules and to a _rationalization_ of the whole platform. During this restyling, we will provide some admin pages in order to manage the initialization of data (e.g., a medical centers, projects, etc.). Besides, we plan to upgrade the system to the latest version of Django an to Python 3.

In the meanwhile, data must be placed in the right place to make the system work properly. We have created a couple of scripts for simplifying that kind of tasks (you can find them in [./web/adminScripts](web/adminScripts)).

Further information below.

## Medical Centers (a.k.a. Institutions)

A `Medical Center` represents a place like a medical center or a generic institution. Related data are managed both by the `biobank` (as Sources) and by the `clinicalManager` module (as Institutions) with some annoying data denormalizations.

Related tables in MySQL are:
* biobank: `biobanca.source`
* clinicalManager: `clinical.coreInstitution_institution;`

In the neo4j graph, Medical Center nodes are labelled as `Institution`. If you want to get them, try the Cypher query below:

    MATCH (n:Institution) RETURN n

### Creating a new Medical Center
For creating a medical center you need 2 pieces of information:
* the name (e.g., _Addenbrookes_)
* the internal name (a kind of id. We usually use a 2-characters-long string e.g., _AA_)

In order to create **all required data**, run `createMedicalCenter.sh`. Here is an example.

Run the script
```bash
$ docker-compose run web bash /adminScripts/createMedicalCenter.sh
```

You will be prompted for medical center `name`. In this example we are going to type: **_The Hospital_**

```
Hello there, you are going to create a new Medical Center...

Enter the name of the medical center (e.g., Addenbrookes) and press [ENTER]:
The Hospital
```
Then, you will be prompted for medical center `internal name`. In this example we are going to type: **_ZZ_**
```
Enter the 2-characters internal name of the medical center  (e.g., AB) and press [ENTER]:
ZZ
```
A final output message, similar to the one below, should confirm that all worked fine.
```
Medical Center created in biobank
	name: The Hospital
	type: Hospital
	internalName: ZZ

/srv/www/clinicalManager/corePatient/models.py:7: RemovedInDjango18Warning: `WgObjectManager.get_query_set` method should be renamed `get_queryset`.
  class WgObjectManager(models.Manager):

Medical Center created in clinicalManager
	name: The Hospital
	institutionType: Medical Center
	identifier: ZZ
```

Please, ignore the warning message. It's due to the deprecation of a method.

Great! You are done!!

### How to check if everything is fine

In MySQL
```
mysql> select * from biobanca.source where internalName = 'ZZ';
+-----+--------------+----------+--------------+
| id  | name         | type     | internalName |
+-----+--------------+----------+--------------+
| 147 | The Hospital | Hospital | ZZ           |
+-----+--------------+----------+--------------+
1 row in set (0.00 sec)
mysql> select * from clinical.coreInstitution_institution where identifier = 'ZZ';
+----+------------+--------------+-----------------+
| id | identifier | name         | institutionType |
+----+------------+--------------+-----------------+
| 85 | ZZ         | The Hospital | Medical Center  |
+----+------------+--------------+-----------------+
1 row in set (0.00 sec)
```

In neo4j

```
MATCH (n:Institution {identifier :'ZZ'}) RETURN n
```
You should get your brand new medical center.


## How to link a Medical Center to a Project
See the Project section below.

# Projects (a.k.a. Protocols or Trials)

A `Project` represents a Trial, a Protocol or something similar. Also in this case, related data are managed both by the biobank (as CollectionProtocols) and by the clinicalManager module (as Projects).

Related tables in MySQL are:
* biobank: `biobanca.collectionprotocol`
* clinicalManager: `clinical.coreProject_project`

In the neo4j graph, they are represented as nodes labelled as `Project`. Let's try to get them all:

    MATCH (n:Project) RETURN n

## Creating a new Project

For creating a Project you need 3 pieces of information:

* the title (e.g., _The Project Foo_)
* the id (e.g., _TheProjectFoo_)
* the owner working group (e.g., _rootpi_WG_)

NB: the owner working group will not affect the project visibility during collections in biobank. It has been placed there for future improvements.

In order to create all required data, run `createProject.sh`. Here is an example.

Run the script

```
$ docker-compose run web bash /adminScripts/createProject.sh
```
You will be prompted for project `title`. In this example we are going to type: **_The New Project_**
```
Creating a new Project (aka protocol)...

Enter the title of the Project (e.g., The Project Foo) and press [ENTER]:
The New Project
```
Then, you will be prompted for project `id`. In this example we are going to type: **_The_new_proj_**
```
Enter the id of the Project (e.g., TheProjectFoo) and press [ENTER]:
The_new_proj
```
Finally, you will be asked to pick the `WG` which owns the Project. In this example we are going to type: **_Medico_WG_**
```
Enter the wg which owns the Project (e.g., rootpi_WG) and press [ENTER]:
Medico_WG
```
A final output message, similar to the one below, should confirm that everithing is fine.
```
Project created in biobank

/srv/www/clinicalManager/corePatient/models.py:7: RemovedInDjango18Warning: `WgObjectManager.get_query_set` method should be renamed `get_queryset`.
  class WgObjectManager(models.Manager):

Project created in clinicalManager
```

Please, ignore the warning message. It's due to a deprecation of a `Django` method.

Mission accomplished!

### How to check if everything is fine
In MySQL

```
mysql> select * from biobanca.collectionprotocol where project = 'The_new_proj';
+----+--------------+-----------------+--------------+--------------------+-----------------+----------------------------+------------------+------------------+--------------+
| id | name         | title           | project      | projectDateRelease | informedConsent | informedConsentDateRelease | ethicalCommittee | approvalDocument | approvalDate |
+----+--------------+-----------------+--------------+--------------------+-----------------+----------------------------+------------------+------------------+--------------+
| 30 | The_new_proj | The New Project | The_new_proj | 2017-12-06         |                 | 2017-12-06                 |                  |                  | 2017-12-06   |
+----+--------------+-----------------+--------------+--------------------+-----------------+----------------------------+------------------+------------------+--------------+
1 row in set (0.00 sec)

mysql> select * from clinical.coreProject_project where identifier='The_new_proj';
+----+--------------+-----------------+
| id | identifier   | name            |
+----+--------------+-----------------+
| 25 | The_new_proj | The New Project |
+----+--------------+-----------------+
1 row in set (0.00 sec)
```

In neo4j

    MATCH (n:Project {identifier :'The_new_proj'})-[r:OwnsData]-(w:WG) RETURN n,r,w

You should get your new Project linked to the WG.

## How to Link a Medical Center to a Project

In order to complete the Project creation, you need to link your new Project to one or more Medical Centers. You can do it directly via `Python`.

Make sure you are working in virtualenv `venvdj1.7` and then start an interactive Python session. To achieve this goal, you can use the following command:

```bash
docker-compose run web /virtualenvs/venvdj1.7/bin/ipython
```

Inside the Python shell, run `utils1_7.centersToProjects()`. It takes two arguments: (i) a list of Medical Centers internal names and (ii) a list of Projects ids. It links all passed Projects to all Medical Centers (i.e., Cartesian product). Here an example where we link `ZZ` to `The_new_proj`. Note that we first need to add ```/adminScripts``` to the Python path in order to use the ```utils1_7``` library.
```
In [1]: import sys

In [2]: sys.path.append('/adminScripts')

In [3]: from utils1_7 import centersToProjects
/srv/www/clinicalManager/corePatient/models.py:7: RemovedInDjango18Warning: `WgObjectManager.get_query_set` method should be renamed `get_queryset`.
  class WgObjectManager(models.Manager):


In [4]: centersToProjects(['ZZ'],['The_new_proj'])
linking hospital: ZZ
		...to project: The_new_proj
Project(s) linked to hospital(s)

```

Please, ignore the warning message once again.

That's all!

### How to check if everything is fine

This operation affects only the graph. Use the Cypher query below to get all relations which bind `The_new_proj ` to `Institution` nodes

```
MATCH (i:Institution)-[r:participates]-(n:Project {identifier :'The_new_proj'}) RETURN i,r,n
```
