-- MySQL dump 10.13  Distrib 5.5.22, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: loginman
-- ------------------------------------------------------
-- Server version	5.5.22-0ubuntu1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_bda51c3c` (`group_id`),
  KEY `auth_group_permissions_1e014c8f` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_e4470c6e` (`content_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=52 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add group',1,'add_group'),(2,'Can change group',1,'change_group'),(3,'Can delete group',1,'delete_group'),(4,'Can add permission',2,'add_permission'),(5,'Can change permission',2,'change_permission'),(6,'Can delete permission',2,'delete_permission'),(7,'Can add user',3,'add_user'),(8,'Can change user',3,'change_user'),(9,'Can delete user',3,'delete_user'),(10,'Can add content type',4,'add_contenttype'),(11,'Can change content type',4,'change_contenttype'),(12,'Can delete content type',4,'delete_contenttype'),(13,'Can add session',5,'add_session'),(14,'Can change session',5,'change_session'),(15,'Can delete session',5,'delete_session'),(16,'Can add site',6,'add_site'),(17,'Can change site',6,'change_site'),(18,'Can delete site',6,'delete_site'),(19,'Can add las user',7,'add_lasuser'),(20,'Can change las user',7,'change_lasuser'),(21,'Can delete las user',7,'delete_lasuser'),(22,'Can add las module',8,'add_lasmodule'),(23,'Can change las module',8,'change_lasmodule'),(24,'Can delete las module',8,'delete_lasmodule'),(33,'Can delete resource',13,'delete_resource'),(32,'Can change resource',13,'change_resource'),(31,'Can add resource',13,'add_resource'),(28,'Can add log entry',10,'add_logentry'),(29,'Can change log entry',10,'change_logentry'),(30,'Can delete log entry',10,'delete_logentry'),(34,'Can add nonce',11,'add_nonce'),(35,'Can change nonce',11,'change_nonce'),(36,'Can delete nonce',11,'delete_nonce'),(37,'Can add token',12,'add_token'),(38,'Can change token',12,'change_token'),(39,'Can delete token',12,'delete_token'),(40,'Can add consumer',14,'add_consumer'),(41,'Can change consumer',14,'change_consumer'),(42,'Can delete consumer',14,'delete_consumer'),(43,'Can add user open id',16,'add_useropenid'),(44,'Can change user open id',16,'change_useropenid'),(45,'Can delete user open id',16,'delete_useropenid'),(46,'Can add association',17,'add_association'),(47,'Can change association',17,'change_association'),(48,'Can delete association',17,'delete_association'),(49,'Can add nonce',15,'add_nonce'),(50,'Can change nonce',15,'change_nonce'),(51,'Can delete nonce',15,'delete_nonce');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `password` varchar(128) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM AUTO_INCREMENT=31 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'alberto','','','alberto.grand@ircc.it','pbkdf2_sha256$10000$AlxBbYVmL7Yy$Vjkzhb4UQIz/1L+xR/b5MIPDe0eYKOhVhyOKslFeU+o=',1,1,1,'2012-01-19 15:19:36','2012-01-19 15:19:36'),(2,'admin','','','admin@admin.com','pbkdf2_sha256$10000$rChDHavp9hIs$mY3k3f22Ujc6k7WmbmLFl88hhe7ptlyjZ8Zi6PRQmKc=',1,1,1,'2012-05-21 15:09:47','2012-03-07 13:01:50'),(24,'mario.rossi','Mario','Rossi','mario.rossi@las.com','pbkdf2_sha256$10000$jJWxBJM7Tazh$retb2VfTG2V3Xh6T9QNtQgwmpJUe4xPyM0fq/dQ5NMM=',0,1,0,'2012-05-23 10:39:56','2012-03-08 13:36:34'),(25,'andrea.bianchi','Andrea','Bianchi','andrea.bianchi@las.com','pbkdf2_sha256$10000$mvJuGhSERnTd$CS4WimWcxJx6ZU2AqG/wZc16x3AwvI5XwcJVzhQevn4=',0,1,0,'2012-05-21 14:22:53','2012-03-08 13:37:13'),(26,'alessandro.fiori','Alessandro','Fiori','','pbkdf2_sha256$10000$ythPEJiUuzCX$tjR5bj9LYqHOyEsbbv4v5ySaIp6HDpiV8geDm7NAy/I=',0,1,0,'2012-03-08 14:24:11','2012-03-08 14:23:40'),(27,'utente.prova','','','','pbkdf2_sha256$10000$sLTa7teCn7Do$x3NEemU3erz0TAw2Az6jpysHdp6pbBmr2E6cFv3KKL8=',1,1,0,'2012-03-16 13:59:34','2012-03-13 13:47:01'),(28,'utente.prova2','','','','!',0,1,0,'2012-03-20 14:31:16','2012-03-19 14:13:32'),(29,'utente.prova3','','','','!',0,1,0,'2012-03-20 15:02:37','2012-03-20 14:58:38'),(30,'openiduser','Alberto','Grand','alberto.grand@ircc.it','!',0,1,0,'2012-03-20 16:39:53','2012-03-20 16:39:53');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_fbfc09f1` (`user_id`),
  KEY `auth_user_groups_bda51c3c` (`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_fbfc09f1` (`user_id`),
  KEY `auth_user_user_permissions_1e014c8f` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_openid_associations`
--

DROP TABLE IF EXISTS `c_openid_associations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_openid_associations` (
  `server_url` blob NOT NULL,
  `handle` varchar(255) NOT NULL,
  `secret` blob NOT NULL,
  `issued` int(11) NOT NULL,
  `lifetime` int(11) NOT NULL,
  `assoc_type` varchar(64) NOT NULL,
  PRIMARY KEY (`server_url`(255),`handle`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_openid_associations`
--

LOCK TABLES `c_openid_associations` WRITE;
/*!40000 ALTER TABLE `c_openid_associations` DISABLE KEYS */;
/*!40000 ALTER TABLE `c_openid_associations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_openid_nonces`
--

DROP TABLE IF EXISTS `c_openid_nonces`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_openid_nonces` (
  `server_url` blob NOT NULL,
  `timestamp` int(11) NOT NULL,
  `salt` char(40) NOT NULL,
  PRIMARY KEY (`server_url`(255),`timestamp`,`salt`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_openid_nonces`
--

LOCK TABLES `c_openid_nonces` WRITE;
/*!40000 ALTER TABLE `c_openid_nonces` DISABLE KEYS */;
/*!40000 ALTER TABLE `c_openid_nonces` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_fbfc09f1` (`user_id`),
  KEY `django_admin_log_e4470c6e` (`content_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=94 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2012-03-07 14:56:09',2,7,'1','LASUser object',3,''),(2,'2012-03-07 15:11:47',2,7,'mario.rossi','LASUser object',1,''),(3,'2012-03-07 15:12:32',2,7,'andrea.bianchi','LASUser object',1,''),(4,'2012-03-07 15:24:41',2,8,'1','Xeno Management Module',1,''),(5,'2012-03-07 15:26:34',2,8,'2','Bio Banking Managament Module',1,''),(9,'2012-03-07 15:54:04',2,8,'2','Bio Banking Managament Module',1,''),(8,'2012-03-07 15:53:52',2,8,'1','Xeno Management Module',1,''),(10,'2012-03-07 15:54:06',2,7,'mario.rossi','mario.rossi',1,''),(11,'2012-03-07 15:54:40',2,7,'andrea.bianchi','andrea.bianchi',1,''),(12,'2012-03-07 15:55:29',2,7,'andrea.bianchi','andrea.bianchi',2,'No fields changed.'),(13,'2012-03-07 15:55:37',2,7,'andrea.bianchi','andrea.bianchi',2,'Changed modules.'),(14,'2012-03-07 15:55:43',2,7,'andrea.bianchi','andrea.bianchi',2,'Changed modules.'),(15,'2012-03-08 09:17:22',2,8,'1','Xeno Management Module',1,''),(16,'2012-03-08 09:17:29',2,8,'2','Bio Banking Managament Module',1,''),(17,'2012-03-08 09:17:31',2,7,'3','mario.rossi',1,''),(18,'2012-03-08 09:18:42',2,7,'4','andrea.bianchi',1,''),(19,'2012-03-08 09:21:38',2,8,'2','Bio Banking Management Module',2,'Changed name.'),(20,'2012-03-08 09:35:48',2,3,'4','andrea.bianchi',3,''),(21,'2012-03-08 09:35:48',2,3,'3','mario.rossi',3,''),(22,'2012-03-08 09:36:16',2,3,'5','mario.rossi',1,''),(23,'2012-03-08 09:36:40',2,3,'5','mario.rossi',2,'Changed password, first_name, last_name and email.'),(24,'2012-03-08 10:01:40',2,3,'5','mario.rossi',3,''),(25,'2012-03-08 10:01:55',2,7,'6','mario.rossi',1,''),(26,'2012-03-08 10:03:04',2,7,'6','mario.rossi',3,''),(27,'2012-03-08 10:03:11',2,7,'7','mario.rossi',1,''),(28,'2012-03-08 10:04:57',2,7,'7','mario.rossi',3,''),(29,'2012-03-08 10:05:04',2,7,'8','mario.rossi',1,''),(30,'2012-03-08 10:12:23',2,7,'8','mario.rossi',3,''),(31,'2012-03-08 10:12:30',2,7,'9','mario.rossi',1,''),(32,'2012-03-08 10:14:11',2,7,'9','mario.rossi',3,''),(33,'2012-03-08 10:14:23',2,7,'10','mario.rossi',1,''),(34,'2012-03-08 10:18:38',2,7,'11','andrea.bianchi',1,''),(35,'2012-03-08 10:49:22',2,3,'11','andrea.bianchi',3,''),(36,'2012-03-08 10:49:22',2,3,'10','mario.rossi',3,''),(37,'2012-03-08 10:50:13',2,3,'12','mario.rossi',1,''),(38,'2012-03-08 12:46:48',2,8,'1','Bio Banking Management Module',1,''),(39,'2012-03-08 12:46:53',2,8,'2','Xeno Management Module',1,''),(40,'2012-03-08 12:51:37',2,3,'13','andrea.bianchi',1,''),(41,'2012-03-08 12:52:28',2,7,'3','andrea.bianchi',2,'Changed modules.'),(42,'2012-03-08 12:52:42',2,3,'13','andrea.bianchi',3,''),(43,'2012-03-08 12:52:42',2,3,'12','mario.rossi',3,''),(44,'2012-03-08 12:54:31',2,3,'14','mario.rossi',1,''),(45,'2012-03-08 12:54:49',2,7,'4','mario.rossi',3,''),(46,'2012-03-08 12:55:02',2,7,'5','mario.rossi',1,''),(47,'2012-03-08 12:55:11',2,7,'5','mario.rossi',3,''),(48,'2012-03-08 12:55:19',2,3,'14','mario.rossi',3,''),(49,'2012-03-08 12:55:33',2,3,'15','mario.rossi',1,''),(50,'2012-03-08 12:58:54',2,7,'6','mario.rossi',3,''),(51,'2012-03-08 12:59:05',2,7,'7','mario.rossi',1,''),(52,'2012-03-08 12:59:27',2,7,'7','mario.rossi',3,''),(53,'2012-03-08 12:59:46',2,3,'15','mario.rossi',3,''),(54,'2012-03-08 13:00:40',2,3,'16','mario.rossi',1,''),(55,'2012-03-08 13:02:59',2,3,'16','mario.rossi',3,''),(56,'2012-03-08 13:03:30',2,3,'17','mario.rossi',1,''),(57,'2012-03-08 13:03:33',2,7,'9','mario.rossi',1,''),(58,'2012-03-08 13:03:42',2,3,'18','andrea.bianchi',1,''),(59,'2012-03-08 13:04:08',2,7,'10','andrea.bianchi',1,''),(60,'2012-03-08 13:29:07',2,7,'19','mario.rossi',1,''),(61,'2012-03-08 13:30:09',2,7,'19','mario.rossi',3,''),(62,'2012-03-08 13:30:21',2,7,'20','mario.rossi',1,''),(63,'2012-03-08 13:31:17',2,7,'20','mario.rossi',3,''),(64,'2012-03-08 13:31:25',2,7,'21','mario.rossi',1,''),(65,'2012-03-08 13:34:06',2,7,'21','mario.rossi',3,''),(66,'2012-03-08 13:34:18',2,7,'22','mario.rossi',1,''),(67,'2012-03-08 13:34:53',2,7,'22','mario.rossi',3,''),(68,'2012-03-08 13:35:01',2,7,'23','mario.rossi',1,''),(69,'2012-03-08 13:36:08',2,7,'23','mario.rossi',3,''),(70,'2012-03-08 13:36:16',2,8,'1','Xeno Management Module',1,''),(71,'2012-03-08 13:36:24',2,8,'2','Bio Banking Management Module',1,''),(72,'2012-03-08 13:36:34',2,7,'24','mario.rossi',1,''),(73,'2012-03-08 13:37:04',2,7,'24','mario.rossi',2,'Changed password, modules, first_name, last_name and email.'),(74,'2012-03-08 13:37:13',2,7,'25','andrea.bianchi',1,''),(75,'2012-03-08 13:37:27',2,7,'25','andrea.bianchi',2,'Changed password, modules, first_name, last_name and email.'),(76,'2012-03-08 14:23:40',2,7,'26','alessandro.fiori',1,''),(77,'2012-03-08 14:23:56',2,7,'26','alessandro.fiori',2,'Changed password, modules, first_name and last_name.'),(78,'2012-03-13 13:37:52',2,8,'1','Xeno Management Module',2,'Changed url.'),(79,'2012-03-13 13:38:02',2,8,'2','Bio Banking Management Module',2,'Changed url.'),(80,'2012-03-13 13:41:19',2,8,'1','Xeno Management Module',2,'Changed url.'),(81,'2012-03-13 13:41:24',2,8,'2','Bio Banking Management Module',2,'Changed url.'),(82,'2012-03-13 13:47:01',2,7,'27','utente.prova',1,''),(83,'2012-03-13 13:47:13',2,7,'27','utente.prova',2,'Changed password, modules and is_staff.'),(84,'2012-03-13 15:23:27',2,8,'1','Xeno Management Module',2,'Changed url.'),(85,'2012-03-13 15:23:31',2,8,'2','Bio Banking Management Module',2,'Changed url.'),(86,'2012-03-14 16:18:06',2,8,'1','Xeno Management Module',2,'Changed url.'),(87,'2012-03-14 16:18:12',2,8,'2','Bio Banking Management Module',2,'Changed url.'),(88,'2012-03-14 16:20:44',2,8,'1','Xeno Management Module',2,'Changed url.'),(89,'2012-03-14 16:20:50',2,8,'2','Bio Banking Management Module',2,'Changed url.'),(90,'2012-03-15 15:16:44',2,8,'1','Xeno Management Module',2,'Changed url.'),(91,'2012-03-15 15:16:50',2,8,'2','Bio Banking Management Module',2,'Changed url.'),(92,'2012-03-15 15:33:15',2,8,'1','Xeno Management Module',2,'Changed url.'),(93,'2012-03-15 15:33:19',2,8,'2','Bio Banking Management Module',2,'Changed url.');
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=MyISAM AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'group','auth','group'),(2,'permission','auth','permission'),(3,'user','auth','user'),(4,'content type','contenttypes','contenttype'),(5,'session','sessions','session'),(6,'site','sites','site'),(7,'las user','loginmanager','lasuser'),(8,'las module','loginmanager','lasmodule'),(11,'nonce','piston','nonce'),(10,'log entry','admin','logentry'),(12,'token','piston','token'),(13,'resource','piston','resource'),(14,'consumer','piston','consumer'),(15,'nonce','django_openid_auth','nonce'),(16,'user open id','django_openid_auth','useropenid'),(17,'association','django_openid_auth','association');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_openid_auth_association`
--

DROP TABLE IF EXISTS `django_openid_auth_association`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_openid_auth_association` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_url` longtext NOT NULL,
  `handle` varchar(255) NOT NULL,
  `secret` longtext NOT NULL,
  `issued` int(11) NOT NULL,
  `lifetime` int(11) NOT NULL,
  `assoc_type` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_openid_auth_association`
--

LOCK TABLES `django_openid_auth_association` WRITE;
/*!40000 ALTER TABLE `django_openid_auth_association` DISABLE KEYS */;
INSERT INTO `django_openid_auth_association` VALUES (1,'http://localhost:9000/openidserver','{HMAC-SHA1}{4f673f08}{ckXOLQ==}','Uj2U76ri7PkG1sep8KGMICCBfFQ=\n',1332166408,1209600,'HMAC-SHA1'),(2,'http://guadalupa.polito.it:8000/openidserver','{HMAC-SHA1}{4f689b18}{NoHfIw==}','7/SvMLEB5JMAUWHYHMvIuy8S1CY=\n',1332255514,1209600,'HMAC-SHA1'),(3,'https://www.google.com/accounts/o8/ud','AMlYA9WEbLz5Ef03w5OclgWm7i4fxbazkOz3dP8QtFgTqf70tHpIyvk8','scg2sd3tOgwI6BVSKa5fxcY01a0=\n',1332261560,46800,'HMAC-SHA1');
/*!40000 ALTER TABLE `django_openid_auth_association` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_openid_auth_nonce`
--

DROP TABLE IF EXISTS `django_openid_auth_nonce`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_openid_auth_nonce` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_url` varchar(2047) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `salt` varchar(40) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_openid_auth_nonce`
--

LOCK TABLES `django_openid_auth_nonce` WRITE;
/*!40000 ALTER TABLE `django_openid_auth_nonce` DISABLE KEYS */;
INSERT INTO `django_openid_auth_nonce` VALUES (1,'http://localhost:9000/openidserver',1332166412,'C8NdRV'),(2,'http://localhost:9000/openidserver',1332166495,'7zThWR'),(3,'http://localhost:9000/openidserver',1332166586,'cUKU2u'),(4,'http://localhost:9000/openidserver',1332166669,'ovmrbJ'),(5,'http://localhost:9000/openidserver',1332167230,'AV7nXO'),(6,'http://localhost:9000/openidserver',1332253876,'XfSXPI'),(7,'http://guadalupa.polito.it:8000/openidserver',1332255517,'ycDYcc'),(8,'http://guadalupa.polito.it:8000/openidserver',1332255755,'5cOVfi'),(9,'https://www.google.com/accounts/o8/ud',1332261585,'N3tAWmzkbjxJSQ');
/*!40000 ALTER TABLE `django_openid_auth_nonce` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_openid_auth_useropenid`
--

DROP TABLE IF EXISTS `django_openid_auth_useropenid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_openid_auth_useropenid` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `claimed_id` longtext NOT NULL,
  `display_id` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_openid_auth_useropenid_fbfc09f1` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_openid_auth_useropenid`
--

LOCK TABLES `django_openid_auth_useropenid` WRITE;
/*!40000 ALTER TABLE `django_openid_auth_useropenid` DISABLE KEYS */;
INSERT INTO `django_openid_auth_useropenid` VALUES (1,28,'http://localhost:9000/id/utente.prova','http://localhost:9000/id/utente.prova'),(2,29,'http://guadalupa.polito.it:8000/id/utente.prova','http://guadalupa.polito.it:8000/id/utente.prova'),(3,30,'https://www.google.com/accounts/o8/id?id=AItOawmLWdxFQq13FFt9DjgBkyBcpCw6BpOFieA','https://www.google.com/accounts/o8/id?id=AItOawmLWdxFQq13FFt9DjgBkyBcpCw6BpOFieA');
/*!40000 ALTER TABLE `django_openid_auth_useropenid` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_c25c2c28` (`expire_date`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('a04ee8e5f02874c8af8ee3d4d1ffc69d','YzBjY2JiZmNmZWRlNjA4ZjNmNzdkMjEyNDFlNmViOTllZmJlM2M5NzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARl1Lg==\n','2012-03-23 14:11:18'),('ff35c8f6c1667107846dd59ede320a71','NWFhYjY1ZmNjMWEzMWM0MGZiMjY0ZjU4Yzg0ZmQ3ZGRjNjBkMzY4MTqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKAQJ1Lg==\n','2012-03-21 14:54:21'),('b8cb1a5f48ab2180558897314be675ad','MjE3ODdkZWM5Y2FmNDg4MDNmMzA2Zjg4YjI4NjVhMjMyNmYxM2M1ZTqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARh1Lg==\n','2012-03-23 14:27:02'),('c773cf7ed7354a9b3e00c11d281c1e84','MjE3ODdkZWM5Y2FmNDg4MDNmMzA2Zjg4YjI4NjVhMjMyNmYxM2M1ZTqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARh1Lg==\n','2012-03-23 14:53:29'),('5aa35e6373b8c648dbfd8b97d67cb243','NTE5NGQ5NWYxYzcxYjY3OGUxYzI3YjIyY2I2YzQ1MzM5OTEwNGU2ODqAAn1xAShVDV9hdXRoX3Vz\nZXJfaWSKARhVEl9hdXRoX3VzZXJfYmFja2VuZFUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5k\ncy5Nb2RlbEJhY2tlbmRxAnUu\n','2012-03-23 16:38:30'),('0358ca1ea5e1b98334c65d5d78ec1d1b','MjE3ODdkZWM5Y2FmNDg4MDNmMzA2Zjg4YjI4NjVhMjMyNmYxM2M1ZTqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARh1Lg==\n','2012-03-23 16:36:57'),('8bf4489acf4c0cdb3cd6afd1ddf0afee','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-27 14:43:26'),('6800fc8146d7343881bd30e236bb7bd8','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-27 15:20:37'),('bd0e5124980c24c8478a49a3fcf1694f','MTg1NTg2M2M2MDdlYTE0ZDlmMTM4ZDQ0N2RjY2I5MzZhM2FjZDk2MTqAAn1xAVUKdGVzdGNvb2tp\nZXECVQZ3b3JrZWRxA3Mu\n','2012-03-27 15:21:17'),('f99bc3f95125985502f0689262f4350f','OTVlYWMwYmNlNDY5MWE1Y2U3MTIxNWQyNWEzYzZkNGJhNjYyNmYxNTqAAn1xAShVDV9hdXRoX3Vz\nZXJfaWSKARtVEl9hdXRoX3VzZXJfYmFja2VuZFUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5k\ncy5Nb2RlbEJhY2tlbmRxAnUu\n','2012-03-27 17:17:51'),('e34924d13bd4e80e2407d9e1a5553779','OTVlYWMwYmNlNDY5MWE1Y2U3MTIxNWQyNWEzYzZkNGJhNjYyNmYxNTqAAn1xAShVDV9hdXRoX3Vz\nZXJfaWSKARtVEl9hdXRoX3VzZXJfYmFja2VuZFUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5k\ncy5Nb2RlbEJhY2tlbmRxAnUu\n','2012-03-29 12:43:29'),('bc96f020f8e224b1255aa0c0a03cd43b','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-27 16:01:53'),('cc10673ed4c54812982be8bbd7d996d0','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-27 16:02:52'),('76764b35815e7f02f01a19ede834d59d','MWQ3YTE5ZmI3OWZkNDI3Nzc4NTI0NmFhYzM0NWVhYjI0Y2Q4ZWExZTqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZFUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmRxAlUN\nX2F1dGhfdXNlcl9pZIoBG3Uu\n','2012-03-29 11:17:08'),('c080b848410f4907c3f150245fc043c8','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 14:13:25'),('7d0da6e4633fa71ca89e06d6f23edcb8','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 14:10:54'),('3a13aa1b32835096557ed9bcd21be92a','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 14:05:17'),('72ef33e04a5800dec6a4be6b7134b8d3','OTVlYWMwYmNlNDY5MWE1Y2U3MTIxNWQyNWEzYzZkNGJhNjYyNmYxNTqAAn1xAShVDV9hdXRoX3Vz\nZXJfaWSKARtVEl9hdXRoX3VzZXJfYmFja2VuZFUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5k\ncy5Nb2RlbEJhY2tlbmRxAnUu\n','2012-03-29 13:48:55'),('911fdccbc5078ea33ac290aa39bbe3ea','NWFhYjY1ZmNjMWEzMWM0MGZiMjY0ZjU4Yzg0ZmQ3ZGRjNjBkMzY4MTqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKAQJ1Lg==\n','2012-03-29 11:02:43'),('50460d7188c691b9654ef86f8ebe79e0','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 15:07:35'),('e6957a7835ce69ed7b393ba42bdb10ea','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 14:20:44'),('86a6f29ecbba501664fc7eda5e599ae5','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 14:21:08'),('eefe0a946b58fb43667a5fddd378aac6','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 14:21:22'),('f7a53050bac593272ef8f838c02dfc78','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 15:14:09'),('e04fd6becc48c58813f4de8034facdfb','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 15:14:19'),('9b791ed493d87395ab008bf9f328e20a','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 15:18:30'),('2795469583bce61e75433d97df567c33','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 15:17:26'),('f1d414476527472af8dca7843a81b33a','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 15:33:29'),('bb0b56c4a3e0863c06f80ca69639a70d','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 15:36:11'),('3036c663d38c5185c6f744095ef2e6af','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 15:48:10'),('48d43b946c27e5363b0601b5f82683b1','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 16:10:57'),('f2c0f39bb33822879878ae187d41aca2','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 16:11:32'),('5703fccc7b552957089f2b16a1ab89f3','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-29 16:22:56'),('1b09bde9f56506d419f8205df3b6da28','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-30 13:56:30'),('11e0ebe1b3e6c51116d1e776d548071c','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-30 11:00:16'),('cd991c1a1b1a052cb2aeb00ff9b66221','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-30 13:57:00'),('a28ed67db10ce099fb4d74e2aabffd28','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-30 13:57:28'),('ea21479b4a8563de399beaffa977e18c','NTgyNGRkNTNjMmJlNmRhNzA1NGQwZGEzYTZhZGY2ZmQ3ZmE4ZjlkMzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARt1Lg==\n','2012-03-30 13:59:34'),('a8bc18feee04aee6962cc57da4c2e876','ZDY3MGUyNjRmNTg2OTY0YzU2ODM0YWRkZDI5MGQ0NTU4MmIxOGI5ODqAAn1xAShVBk9QRU5JRH1V\nEl9hdXRoX3VzZXJfYmFja2VuZHECVSVkamFuZ29fb3BlbmlkX2F1dGguYXV0aC5PcGVuSURCYWNr\nZW5kcQNVDV9hdXRoX3VzZXJfaWRxBIoBHHUu\n','2012-04-02 14:13:32'),('a61a665185526c80748dc86daaa71342','YTUxNWIzZWQ5ODM4NGVlMDA3N2YwYWNiZjcyN2MwNDI0NDdlYzg0NTqAAn1xAShVBk9QRU5JRHEC\nfVUSX2F1dGhfdXNlcl9iYWNrZW5kcQNVJWRqYW5nb19vcGVuaWRfYXV0aC5hdXRoLk9wZW5JREJh\nY2tlbmRxBFUNX2F1dGhfdXNlcl9pZHEFigEcdS4=\n','2012-04-02 14:16:26'),('bb4a5fa19d1098bcd450c6acd117c63d','OGNiMTZjNDM2Mjc0MjNjZWQyYTM2MzAxYWRkNTkzNmMwYzQxOGQ5MTqAAn1xAShVBk9QRU5JRH1V\nEl9hdXRoX3VzZXJfYmFja2VuZHECVSVkamFuZ29fb3BlbmlkX2F1dGguYXV0aC5PcGVuSURCYWNr\nZW5kcQNVDV9hdXRoX3VzZXJfaWRxBIoBHnUu\n','2012-04-03 16:39:53'),('8c522c6b4fdd6eaad6e65d7cb21f4a52','NWFhYjY1ZmNjMWEzMWM0MGZiMjY0ZjU4Yzg0ZmQ3ZGRjNjBkMzY4MTqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKAQJ1Lg==\n','2012-04-02 14:24:39'),('fa4b4af14cb315ff6212756c24235961','ZmE4MzAxYjZlYTMyZjczNzBlZTYxOWJkMGI0YTQ1Yjk3ZjlmNzY2ODqAAn1xAVUGT1BFTklEcQJ9\ncy4=\n','2012-04-03 16:38:03'),('9ab0644f76d89f0193e759708d192958','MWI5ZjhlMWE0ZmZkMDk2OThmNGI2ODZjM2FmY2NkYmExMThjNzcyODqAAn1xAVUGT1BFTklEcQJ9\ncQMoVSFfeWFkaXNfc2VydmljZXNfX29wZW5pZF9jb25zdW1lcl9xBGNvcGVuaWQueWFkaXMubWFu\nYWdlcgpZYWRpc1NlcnZpY2VNYW5hZ2VyCnEFKYFxBn1xByhVCHNlcnZpY2VzcQhdVQl5YWRpc191\ncmxxCVUlaHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS9hY2NvdW50cy9vOC9pZFUMc3RhcnRpbmdfdXJs\ncQpVJWh0dHBzOi8vd3d3Lmdvb2dsZS5jb20vYWNjb3VudHMvbzgvaWRxC1ULc2Vzc2lvbl9rZXlx\nDGgEVQhfY3VycmVudHENY29wZW5pZC5jb25zdW1lci5kaXNjb3ZlcgpPcGVuSURTZXJ2aWNlRW5k\ncG9pbnQKcQ4pgXEPfXEQKFUKY2xhaW1lZF9pZHERTlUSZGlzcGxheV9pZGVudGlmaWVycRJOVQpz\nZXJ2ZXJfdXJscRNVJWh0dHBzOi8vd3d3Lmdvb2dsZS5jb20vYWNjb3VudHMvbzgvdWRVC2Nhbm9u\naWNhbElEcRROVQhsb2NhbF9pZHEVTlUJdHlwZV91cmlzcRZdcRcoVSdodHRwOi8vc3BlY3Mub3Bl\nbmlkLm5ldC9hdXRoLzIuMC9zZXJ2ZXJxGFUcaHR0cDovL29wZW5pZC5uZXQvc3J2L2F4LzEuMHEZ\nVTRodHRwOi8vc3BlY3Mub3BlbmlkLm5ldC9leHRlbnNpb25zL3VpLzEuMC9tb2RlL3BvcHVwcRpV\nLmh0dHA6Ly9zcGVjcy5vcGVuaWQubmV0L2V4dGVuc2lvbnMvdWkvMS4wL2ljb25xG1UraHR0cDov\nL3NwZWNzLm9wZW5pZC5uZXQvZXh0ZW5zaW9ucy9wYXBlLzEuMHEcZVUKdXNlZF95YWRpc3EdiHVi\ndWJVG19vcGVuaWRfY29uc3VtZXJfbGFzdF90b2tlbmgPdXMu\n','2012-04-03 16:41:32'),('a59a92f42e69a4e3d0575e56668a00d5','ZDY3MGUyNjRmNTg2OTY0YzU2ODM0YWRkZDI5MGQ0NTU4MmIxOGI5ODqAAn1xAShVBk9QRU5JRH1V\nEl9hdXRoX3VzZXJfYmFja2VuZHECVSVkamFuZ29fb3BlbmlkX2F1dGguYXV0aC5PcGVuSURCYWNr\nZW5kcQNVDV9hdXRoX3VzZXJfaWRxBIoBHHUu\n','2012-04-02 14:14:55'),('61bf5790220ab6de3f9dbef76e521906','ZDY3MGUyNjRmNTg2OTY0YzU2ODM0YWRkZDI5MGQ0NTU4MmIxOGI5ODqAAn1xAShVBk9QRU5JRH1V\nEl9hdXRoX3VzZXJfYmFja2VuZHECVSVkamFuZ29fb3BlbmlkX2F1dGguYXV0aC5PcGVuSURCYWNr\nZW5kcQNVDV9hdXRoX3VzZXJfaWRxBIoBHHUu\n','2012-04-02 14:27:10'),('ec42829ac38f38c369549cec7b699a58','ZDY3MGUyNjRmNTg2OTY0YzU2ODM0YWRkZDI5MGQ0NTU4MmIxOGI5ODqAAn1xAShVBk9QRU5JRH1V\nEl9hdXRoX3VzZXJfYmFja2VuZHECVSVkamFuZ29fb3BlbmlkX2F1dGguYXV0aC5PcGVuSURCYWNr\nZW5kcQNVDV9hdXRoX3VzZXJfaWRxBIoBHHUu\n','2012-04-03 14:31:16'),('e27411595c503b434874519f6cc46ff3','ZTBiZjQ5MjQ3NmQzNDcyYWEwOTkyMzZmZDgyYjA2YmRmNWZhOTI2YTqAAn1xAShVBk9QRU5JRH1V\nEl9hdXRoX3VzZXJfYmFja2VuZHECVSVkamFuZ29fb3BlbmlkX2F1dGguYXV0aC5PcGVuSURCYWNr\nZW5kcQNVDV9hdXRoX3VzZXJfaWRxBIoBHXUu\n','2012-04-03 14:58:38'),('d2cefd35c46ab20b944c9bceaa87d2d9','ZTBiZjQ5MjQ3NmQzNDcyYWEwOTkyMzZmZDgyYjA2YmRmNWZhOTI2YTqAAn1xAShVBk9QRU5JRH1V\nEl9hdXRoX3VzZXJfYmFja2VuZHECVSVkamFuZ29fb3BlbmlkX2F1dGguYXV0aC5PcGVuSURCYWNr\nZW5kcQNVDV9hdXRoX3VzZXJfaWRxBIoBHXUu\n','2012-04-03 15:02:37'),('7bb0b9c1fa8be599ddde681f6b08aeb4','NDc2NmEyZjVhYWU2YjhhYjc5NzAxYjI5Zjg1OTFkNmNlZWUxZDI1ZTqAAn1xAShVIV95YWRpc19z\nZXJ2aWNlc19fb3BlbmlkX2NvbnN1bWVyX3ECY29wZW5pZC55YWRpcy5tYW5hZ2VyCllhZGlzU2Vy\ndmljZU1hbmFnZXIKcQMpgXEEfXEFKFUIc2VydmljZXNxBl1VCXlhZGlzX3VybHEHVSJodHRwOi8v\nbG9jYWxob3N0OjgwMDAvc2VydmVyL3VzZXIvVQxzdGFydGluZ191cmxxCFgaAAAAbG9jYWxob3N0\nOjgwMDAvc2VydmVyL3VzZXJVC3Nlc3Npb25fa2V5cQloAlUIX2N1cnJlbnRxCmNvcGVuaWQuY29u\nc3VtZXIuZGlzY292ZXIKT3BlbklEU2VydmljZUVuZHBvaW50CnELKYFxDH1xDShVCmNsYWltZWRf\naWRxDlUiaHR0cDovL2xvY2FsaG9zdDo4MDAwL3NlcnZlci91c2VyL1USZGlzcGxheV9pZGVudGlm\naWVycQ9OVQpzZXJ2ZXJfdXJscRBVJmh0dHA6Ly9sb2NhbGhvc3Q6ODAwMC9zZXJ2ZXIvZW5kcG9p\nbnQvVQtjYW5vbmljYWxJRHERTlUIbG9jYWxfaWRxEk5VCXR5cGVfdXJpc3ETXXEUVRxodHRwOi8v\nb3BlbmlkLm5ldC9zaWdub24vMS4xcRVhVQp1c2VkX3lhZGlzcRaJdWJ1YlUbX29wZW5pZF9jb25z\ndW1lcl9sYXN0X3Rva2VuaAx1Lg==\n','2012-05-16 09:30:59'),('9e528b98f9681215c904a1a5e64dd959','MjBhOWU4MzY0MWEwNmI1YzczMzg3MTA0ZDJhZGE3YzViOGJkYTMwZTqAAn1xAShVIV95YWRpc19z\nZXJ2aWNlc19fb3BlbmlkX2NvbnN1bWVyX3ECY29wZW5pZC55YWRpcy5tYW5hZ2VyCllhZGlzU2Vy\ndmljZU1hbmFnZXIKcQMpgXEEfXEFKFUIc2VydmljZXNxBl1xB2NvcGVuaWQuY29uc3VtZXIuZGlz\nY292ZXIKT3BlbklEU2VydmljZUVuZHBvaW50CnEIKYFxCX1xCihVCmNsYWltZWRfaWRxC1UiaHR0\ncDovL2xvY2FsaG9zdDo4MDAwL3NlcnZlci91c2VyL3EMVRJkaXNwbGF5X2lkZW50aWZpZXJxDU5V\nCnNlcnZlcl91cmxxDlUmaHR0cDovL2xvY2FsaG9zdDo4MDAwL3NlcnZlci9lbmRwb2ludC9VC2Nh\nbm9uaWNhbElEcQ9OVQhsb2NhbF9pZHEQTlUJdHlwZV91cmlzcRFdcRJVHGh0dHA6Ly9vcGVuaWQu\nbmV0L3NpZ25vbi8xLjFxE2FVCnVzZWRfeWFkaXNxFIl1YmFVCXlhZGlzX3VybHEVVSJodHRwOi8v\nbG9jYWxob3N0OjgwMDAvc2VydmVyL3VzZXIvVQxzdGFydGluZ191cmxxFlgaAAAAbG9jYWxob3N0\nOjgwMDAvc2VydmVyL3VzZXJxF1ULc2Vzc2lvbl9rZXlxGGgCVQhfY3VycmVudHEZaAgpgXEafXEb\nKGgLaAxoDU5oDlUmaHR0cDovL2xvY2FsaG9zdDo4MDAwL3NlcnZlci9lbmRwb2ludC9oD05oEE5o\nEV1xHFUnaHR0cDovL3NwZWNzLm9wZW5pZC5uZXQvYXV0aC8yLjAvc2lnbm9ucR1haBSJdWJ1YlUb\nX29wZW5pZF9jb25zdW1lcl9sYXN0X3Rva2VuaBp1Lg==\n','2012-05-16 09:32:01'),('5001c0d05766d5531337cea06558d61d','MjBhOWU4MzY0MWEwNmI1YzczMzg3MTA0ZDJhZGE3YzViOGJkYTMwZTqAAn1xAShVIV95YWRpc19z\nZXJ2aWNlc19fb3BlbmlkX2NvbnN1bWVyX3ECY29wZW5pZC55YWRpcy5tYW5hZ2VyCllhZGlzU2Vy\ndmljZU1hbmFnZXIKcQMpgXEEfXEFKFUIc2VydmljZXNxBl1xB2NvcGVuaWQuY29uc3VtZXIuZGlz\nY292ZXIKT3BlbklEU2VydmljZUVuZHBvaW50CnEIKYFxCX1xCihVCmNsYWltZWRfaWRxC1UiaHR0\ncDovL2xvY2FsaG9zdDo4MDAwL3NlcnZlci91c2VyL3EMVRJkaXNwbGF5X2lkZW50aWZpZXJxDU5V\nCnNlcnZlcl91cmxxDlUmaHR0cDovL2xvY2FsaG9zdDo4MDAwL3NlcnZlci9lbmRwb2ludC9VC2Nh\nbm9uaWNhbElEcQ9OVQhsb2NhbF9pZHEQTlUJdHlwZV91cmlzcRFdcRJVHGh0dHA6Ly9vcGVuaWQu\nbmV0L3NpZ25vbi8xLjFxE2FVCnVzZWRfeWFkaXNxFIl1YmFVCXlhZGlzX3VybHEVVSJodHRwOi8v\nbG9jYWxob3N0OjgwMDAvc2VydmVyL3VzZXIvVQxzdGFydGluZ191cmxxFlgaAAAAbG9jYWxob3N0\nOjgwMDAvc2VydmVyL3VzZXJxF1ULc2Vzc2lvbl9rZXlxGGgCVQhfY3VycmVudHEZaAgpgXEafXEb\nKGgLaAxoDU5oDlUmaHR0cDovL2xvY2FsaG9zdDo4MDAwL3NlcnZlci9lbmRwb2ludC9oD05oEE5o\nEV1xHFUnaHR0cDovL3NwZWNzLm9wZW5pZC5uZXQvYXV0aC8yLjAvc2lnbm9ucR1haBSJdWJ1YlUb\nX29wZW5pZF9jb25zdW1lcl9sYXN0X3Rva2VuaBp1Lg==\n','2012-05-16 10:00:51'),('c0d31a6e341022c9d9110e5ab80809ac','ODdkYzJmODU1OTY0OTcxMGVjZGVjNTllMzQ3N2I0ZjdmOGY5NTcxZDqAAn1xAS4=\n','2012-05-25 15:03:55'),('d7e0008a404bc7cb7877ec75a47f7f13','OGI2NjgzNjA5NDUwMDQwODkxNmRlMjcxMmI2MzM0NDQyNTg3Mzk4YjqAAn1xAVUJcmV0dXJuX3Rv\nWCsAAABodHRwOi8vbG9jYWxob3N0OjgwMDAveGVub3BhdGllbnRzL2xsbG9naW4vcQJzLg==\n','2012-05-25 15:35:43'),('81a6c3c18a28eaaf760d773fd77cfb30','ZGM3M2UyNmRiYThmMDNkY2E5NTQ5MzVkOTU0ZWJlY2JmOWNiOTQ1MDqAAn1xAVUJcmV0dXJuX3Rv\ncQJYKQAAAGh0dHA6Ly9sb2NhbGhvc3Q6ODAwMC9hdXRoL2NvbXBsZXRlbG9naW4vcQNzLg==\n','2012-06-03 14:13:44'),('f06e7c00f8bf599392c011fa3cea9704','ODY4OWQ4NGJkNjAyNzQwOTRiYTI2ZDJkNjAwMzc5ZjhjODJmMTExODqAAn1xAShVCXJldHVybl90\nb1grAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL3hlbm9wYXRpZW50cy9sbGxvZ2luL1USX2F1dGhf\ndXNlcl9iYWNrZW5kcQJVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5k\ncQNVDV9hdXRoX3VzZXJfaWRxBIoBAnUu\n','2012-05-25 17:16:04'),('4d55bb8e717075023b50e9a5491b0f6d','ZDZjMWJhNTAyZjU3MTViNzY5NDdjYmIwZjdlYmU2YjM2YmVjOWY1ZjqAAn1xAShVA2FwcHECWAMA\nAABYTU1xA1UOcmVtb3RlX3JlcXVlc3RxBIhVCXJldHVybl90b3EFWCkAAABodHRwOi8vbG9jYWxo\nb3N0OjgwMDAvYXV0aC9jb21wbGV0ZWxvZ2luL3EGVRJyZW1vdGVfc2Vzc2lvbl9rZXlxB1ggAAAA\nMjk4NTFhODNkODE3MTc0MjcxMmFjNDk2MmI3NjhmZGFxCHUu\n','2012-06-03 16:43:17'),('37d70034663f5c8b1e0b7593a9df7fd3','YzEwNmFhYTJiMzk3NGY3NDBlMGVlYjI0MzRjZGE5OGQwMzc2NDZlZTqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAAA0MWQ1NDdlN2E0MThhNjUyM2ZlNDNiOThj\nZmEzNWEyNVUNX2F1dGhfdXNlcl9pZHECigEZVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-03 16:34:27'),('01bddb6d058590413fbbdc15a5985b4f','ODdkYzJmODU1OTY0OTcxMGVjZGVjNTllMzQ3N2I0ZjdmOGY5NTcxZDqAAn1xAS4=\n','2012-06-03 16:24:44'),('4599c0e0a43a9b3113b7307bd7ca66bc','NmY2NDE0NWI3YWI4MDFhNTk4MGUyYTEyYjY2MDA1MDdlZWNhMjViMTqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAABhOGZhNzc0MTU3NTExZTcxOTAyYjBlMzYw\nODhjNDcwOFUNX2F1dGhfdXNlcl9pZHECigEYVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-03 16:36:24'),('7b38fd7362d0fc4eb1f77ecaff1ef8a2','MjE3ODdkZWM5Y2FmNDg4MDNmMzA2Zjg4YjI4NjVhMjMyNmYxM2M1ZTqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARh1Lg==\n','2012-06-03 16:36:04'),('eedfec74479ea72f6d9d0bebe609c3a3','OTY3MDY0NDBlYWI1YzBhNTYwZjQ3NTRiZmM0NTEzMDFlZTc5MGQ3ODqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAAAyNTAyZTE4MWU3NDliZTEyZTliYWE2NTUx\nMzFjYzFhNVUNX2F1dGhfdXNlcl9pZHECigEYVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-03 16:43:07'),('45d09124427c4ebcedf27db934eafe17','YzBjY2JiZmNmZWRlNjA4ZjNmNzdkMjEyNDFlNmViOTllZmJlM2M5NzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARl1Lg==\n','2012-06-03 16:52:05'),('42b1c6f801630f9e0aa9edd8f063e618','MzU4NWRmNWEyMmUyYWNlOThjYmFmMTJiMjM4ZjVhNDI3NTg3YWZhNTqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAABmMzY0ODYxNDdmNWY4ZGQ5YmFjNzRhOTFh\nMWY0ODQxN1UNX2F1dGhfdXNlcl9pZHECigEZVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-03 16:48:54'),('b1b86426610437cae5d02f02a66a8512','YzBjY2JiZmNmZWRlNjA4ZjNmNzdkMjEyNDFlNmViOTllZmJlM2M5NzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARl1Lg==\n','2012-06-03 16:53:54'),('353540d6db03029e485bd965166d4cb3','OGVlZjhiZmQ4OWFmOGZmMDUyNzZkZDA0MDk3ZmM0NTlmZTQwNTJmZjqAAn1xAShVA2FwcHECWAMA\nAABYTU1xA1UOcmVtb3RlX3JlcXVlc3RxBIhVCXJldHVybl90b3EFWCkAAABodHRwOi8vbG9jYWxo\nb3N0OjgwMDAvYXV0aC9jb21wbGV0ZWxvZ2luL3EGVRJyZW1vdGVfc2Vzc2lvbl9rZXlxB1ggAAAA\nYTU4MjBkMTYzYzZhN2E2MjE4NDE5NDJmNTMyYTIwNmJxCHUu\n','2012-06-03 17:06:20'),('01c7eb1d62f7fb26be23565bc812d6d0','YzNkOGRkZDg1NjhhODJiMWU3NTI2OWE3NTJjYzliM2U3OWY5ODIxMDqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAAAyOWFiY2JhYzQ0MThiNTZjNTg1ZWQ4Yjhm\nYTAwMDlhZFUNX2F1dGhfdXNlcl9pZHECigEZVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-03 16:55:40'),('34d7182142bf8b2be9797538a53ccfe2','OGRjMDNmNjZiMWQxYWQ1YTUwMGY5NzZhNjQ5ZjRlZDYzODZjZTBmNzqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAAA5YWExNmFhZjhiMGQ1Nzg1NzEyOWRlNDM4\nMGZmZmI0MlUNX2F1dGhfdXNlcl9pZHECigEZVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-03 17:01:52'),('56c50f33d69fc83725a529eae4a06924','ZmRiNDk5ZGVhNTA1MGY0Yzc3ZjQ3NTk0YTRiOThlODYyOGVlYzViNTqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAAA1YjRiZWFjN2JjY2U1M2JiZDIzNTFiNmJi\nNGRiYjZlNlUNX2F1dGhfdXNlcl9pZHECigEYVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-03 17:04:05'),('4e7056a5c1a4f75db6054e3a3972821c','ZDAxMjE2NWUwMDFjMzRlNWZkMjMyODNiMTJhY2Y3M2UxODJlZGYyMTqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAAA2MzdiMWRlMjA3YjkwZTlmMGE0NGExZTk5\nODJlYTAwNVUNX2F1dGhfdXNlcl9pZHECigEZVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-03 17:05:53'),('cef0ec3501f3e3f18ceb0d188012a36c','MjE3ODdkZWM5Y2FmNDg4MDNmMzA2Zjg4YjI4NjVhMjMyNmYxM2M1ZTqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKARh1Lg==\n','2012-06-04 13:42:21'),('9ccc4633b5313650681bccd7687e43d8','YmRmZTljYzI1NTRlNzAxOGNmOTMyMjJmNDFiYmRmOTFjZjM4Zjg0NjqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAAAxYTE3ZTVjNTZlMzIzODZlMDY4MWZkMjVj\nMjE0MjJlOVUNX2F1dGhfdXNlcl9pZHECigEYVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-03 17:09:56'),('5189826d6fd1b6942ea612a5b0dabd7a','YjgxZTdmOTExNWVlZDc5MjFmMDNlOWI2MDZmYjZlOTEzOGRhMzE0MjqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAAA3ZjM1YjA1NDNiNTdiNjFmN2Y1YzgyZDk3\nOTc4NmFhYVUNX2F1dGhfdXNlcl9pZHECigEYVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-03 17:11:24'),('0fd89cd74626e966e014ba25948873b3','MDE5ZDQyNDk4MTkxNzY5YzI0ZTU4ZWU1NzdiOTcxNTk4YWE4YzMzYTqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAAAwYzllNTQxNmQyNTA0MTljYWVjMjBkNTdk\nZDYzNTYzYVUNX2F1dGhfdXNlcl9pZHECigEYVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-04 13:41:15'),('e7bb8cf57d5daec627e8f26fc22164e6','NGE5NDJlY2QyMmVmMzRkNjdhMDgwOTJiYWE4OTRmNDFjMmY0NTMwMTqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAABkYTYwNzE1MDZlYWU1YzliZmJlYTI0NThi\nOGQwNjRkYVUNX2F1dGhfdXNlcl9pZHECigEYVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-04 16:00:11'),('092f514edb5dada3a5c3707b353c9f2e','M2RlMDdjNGUxZjYwOWU0ODc4NmI0YTU3YTFiMTI3ODhjYjhiOTk1NTqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAAA0ZWFkNmMyOTM1ZDg5OTZiMGEzOWJkNDBh\nYTY0YjcwN1UNX2F1dGhfdXNlcl9pZHECigEYVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-04 14:22:04'),('ae4b1a4063ffaa162998c9e94cec0183','Zjk4NDA1MDhjZThjMWMwMGRjMTBlMjU1NTgxMmFjMjllZTZlN2QyMTqAAn1xAShVA2FwcHECWAMA\nAABYTU1xA1UOcmVtb3RlX3JlcXVlc3RxBIhVCXJldHVybl90b3EFWCkAAABodHRwOi8vbG9jYWxo\nb3N0OjgwMDAvYXV0aC9jb21wbGV0ZWxvZ2luL3EGVRJyZW1vdGVfc2Vzc2lvbl9rZXlxB1ggAAAA\nMDliZTYyMDdiZTdjYzU4NmIzYzI2MjU5YmNlZjAyYjlxCHUu\n','2012-06-04 15:29:52'),('48494f84e44a2da20ad070f14f25c45a','Y2QyNWE0ZDcxNjk2ODBmZmIxM2NhZmU5NWI0YjlhYjFjMGI3YzdkYTqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0cQKIVQlyZXR1cm5fdG9xA1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29t\ncGxldGVsb2dpbi9xBFULc2Vzc2lvbl9rZXlxBVggAAAAZTU2OGRmOGM3OGQxNTYwNGJjZmI1YTZk\nNjRjOGY5NjZxBlUFYXBwaWRxB1gDAAAAWE1NcQh1Lg==\n','2012-06-06 10:40:03'),('95b34da84d5038e98b64b3069033f784','NTBkZWJmMDMyNjE4MjFjYWVhNDBjYTc3OWQ3NDJlNzQ2MzJjNWJmNzqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAAA2N2JiYWFmMWFkOWM3MjZmNGE1NDkxNTUz\nMzIwNDE1MFUNX2F1dGhfdXNlcl9pZHECigEYVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-05 14:33:36'),('880beea3e40a4ada12b0282bf7ae8b4a','YThjNDFkYmQ0YTRjNzIzYmE2Y2E0ZDJlZjE2M2QwMTZjMjM0NTdlMDqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFUScmVtb3RlX3Nlc3Npb25fa2V5WCAAAAAxZjFjMTI3MjNmMWYxOGNmYzJlZjU1NWE1\nOWVkYzY4MFUNX2F1dGhfdXNlcl9pZHECigEYVQNhcHBYAwAAAFhNTVUSX2F1dGhfdXNlcl9iYWNr\nZW5kcQNVKWRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kcQRVCXJldHVy\nbl90b1gpAAAAaHR0cDovL2xvY2FsaG9zdDo4MDAwL2F1dGgvY29tcGxldGVsb2dpbi91Lg==\n','2012-06-05 14:37:24'),('761ddc1ad58eea0ca9513389ac43af15','M2M2NGE1NGQ4ZWIwNWFmMGZmNGNhYTE1NzNmMzRhYTA4NDhiNTAxZDqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFULc2Vzc2lvbl9rZXlYIAAAAGU2ZWFiMDYyNGM4YmQ2ODc5NjU5YTI5YWU2MmUxMzlh\nVQ1fYXV0aF91c2VyX2lkcQKKARhVEl9hdXRoX3VzZXJfYmFja2VuZHEDVSlkamFuZ28uY29udHJp\nYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHEEVQVhcHBpZFgDAAAAWE1NVQlyZXR1cm5fdG9Y\nKQAAAGh0dHA6Ly9sb2NhbGhvc3Q6ODAwMC9hdXRoL2NvbXBsZXRlbG9naW4vdS4=\n','2012-06-05 14:48:01'),('da8fc387cf5f79b093bd585321582812','OGM3NjQ3ZGRkNGQ2NGEyMzM5NGExODFiOTBkZjkxMzUzM2ZkNjJmZDqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFULc2Vzc2lvbl9rZXlYIAAAAGFkNDBhOGNjMzUyOTM5MDcxODhiMmRmNGRhOWEzMjcx\nVQ1fYXV0aF91c2VyX2lkcQKKARhVEl9hdXRoX3VzZXJfYmFja2VuZHEDVSlkamFuZ28uY29udHJp\nYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHEEVQVhcHBpZFgDAAAAWE1NVQlyZXR1cm5fdG9Y\nKQAAAGh0dHA6Ly9sb2NhbGhvc3Q6ODAwMC9hdXRoL2NvbXBsZXRlbG9naW4vdS4=\n','2012-06-05 14:59:27'),('7637b59ae7fe178443a732620bf849b4','ZTc2MTQwNDkwMDQ5ODllYzU1NzE3NWE1OTllYmNjMDM0ZTNjNzZjNzqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFULc2Vzc2lvbl9rZXlYIAAAAGE2YThjNjMzOWEwMjE4MGY3YTVkODIwYWJhNzc5M2Rk\nVQ1fYXV0aF91c2VyX2lkcQKKARhVEl9hdXRoX3VzZXJfYmFja2VuZHEDVSlkamFuZ28uY29udHJp\nYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHEEVQVhcHBpZFgDAAAAWE1NVQlyZXR1cm5fdG9Y\nKQAAAGh0dHA6Ly9sb2NhbGhvc3Q6ODAwMC9hdXRoL2NvbXBsZXRlbG9naW4vdS4=\n','2012-06-06 10:21:22'),('e96f11aa3178bf00cd5fcd39e7af8102','ZWI2NTc1Y2U2NTMxZTY4NDY2MTgzOTFiNmUwMTY3YjlkZGU4Y2JkNzqAAn1xAShVDnJlbW90ZV9y\nZXF1ZXN0iFULc2Vzc2lvbl9rZXlYIAAAAGM0NWU3NDliOTlmY2RkYWVkZjEzZTQ0NjczMzJkYjky\nVQ1fYXV0aF91c2VyX2lkcQKKARhVEl9hdXRoX3VzZXJfYmFja2VuZHEDVSlkamFuZ28uY29udHJp\nYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHEEVQVhcHBpZFgDAAAAWE1NVQlyZXR1cm5fdG9Y\nKQAAAGh0dHA6Ly9sb2NhbGhvc3Q6ODAwMC9hdXRoL2NvbXBsZXRlbG9naW4vdS4=\n','2012-06-06 10:39:56');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES (1,'example.com','example.com');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loginmanager_lasmodule`
--

DROP TABLE IF EXISTS `loginmanager_lasmodule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loginmanager_lasmodule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `url` varchar(128) NOT NULL,
  `shortname` varchar(30) DEFAULT NULL,
  `remote_key` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loginmanager_lasmodule`
--

LOCK TABLES `loginmanager_lasmodule` WRITE;
/*!40000 ALTER TABLE `loginmanager_lasmodule` DISABLE KEYS */;
INSERT INTO `loginmanager_lasmodule` VALUES (1,'Xeno Management Module','http://devircc.polito.it/xeno/api/login','XMM','=!)x>/9q~T~N=B;kqHe#xp/9r<X[-+wC=<KB]V]%-/Q~M*8$o6Vd`OoAal~k3~5]'),(2,'Bio Banking Management Module','http://devircc.polito.it/biobank/api/login','BBMM','');
/*!40000 ALTER TABLE `loginmanager_lasmodule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loginmanager_lasuser`
--

DROP TABLE IF EXISTS `loginmanager_lasuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loginmanager_lasuser` (
  `user_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`user_ptr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loginmanager_lasuser`
--

LOCK TABLES `loginmanager_lasuser` WRITE;
/*!40000 ALTER TABLE `loginmanager_lasuser` DISABLE KEYS */;
INSERT INTO `loginmanager_lasuser` VALUES (24),(25),(26),(27);
/*!40000 ALTER TABLE `loginmanager_lasuser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loginmanager_lasuser_modules`
--

DROP TABLE IF EXISTS `loginmanager_lasuser_modules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loginmanager_lasuser_modules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lasuser_id` int(11) NOT NULL,
  `lasmodule_id` int(11) NOT NULL,
  `remote_user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `lasuser_id` (`lasuser_id`,`lasmodule_id`),
  KEY `loginmanager_lasuser_modules_e0678aba` (`lasuser_id`),
  KEY `loginmanager_lasuser_modules_f6752d1b` (`lasmodule_id`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loginmanager_lasuser_modules`
--

LOCK TABLES `loginmanager_lasuser_modules` WRITE;
/*!40000 ALTER TABLE `loginmanager_lasuser_modules` DISABLE KEYS */;
INSERT INTO `loginmanager_lasuser_modules` VALUES (1,24,1,0),(2,24,2,0),(3,25,2,0),(4,26,1,0),(5,26,2,0),(6,27,1,0),(7,27,2,0);
/*!40000 ALTER TABLE `loginmanager_lasuser_modules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `piston_consumer`
--

DROP TABLE IF EXISTS `piston_consumer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `piston_consumer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `key` varchar(18) NOT NULL,
  `secret` varchar(32) NOT NULL,
  `status` varchar(16) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `piston_consumer_fbfc09f1` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `piston_consumer`
--

LOCK TABLES `piston_consumer` WRITE;
/*!40000 ALTER TABLE `piston_consumer` DISABLE KEYS */;
/*!40000 ALTER TABLE `piston_consumer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `piston_nonce`
--

DROP TABLE IF EXISTS `piston_nonce`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `piston_nonce` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `token_key` varchar(18) NOT NULL,
  `consumer_key` varchar(18) NOT NULL,
  `key` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `piston_nonce`
--

LOCK TABLES `piston_nonce` WRITE;
/*!40000 ALTER TABLE `piston_nonce` DISABLE KEYS */;
/*!40000 ALTER TABLE `piston_nonce` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `piston_resource`
--

DROP TABLE IF EXISTS `piston_resource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `piston_resource` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `url` longtext NOT NULL,
  `is_readonly` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `piston_resource`
--

LOCK TABLES `piston_resource` WRITE;
/*!40000 ALTER TABLE `piston_resource` DISABLE KEYS */;
/*!40000 ALTER TABLE `piston_resource` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `piston_token`
--

DROP TABLE IF EXISTS `piston_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `piston_token` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(18) NOT NULL,
  `secret` varchar(32) NOT NULL,
  `token_type` int(11) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `is_approved` tinyint(1) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `consumer_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `piston_token_fbfc09f1` (`user_id`),
  KEY `piston_token_6565fc20` (`consumer_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `piston_token`
--

LOCK TABLES `piston_token` WRITE;
/*!40000 ALTER TABLE `piston_token` DISABLE KEYS */;
/*!40000 ALTER TABLE `piston_token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `s_openid_associations`
--

DROP TABLE IF EXISTS `s_openid_associations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `s_openid_associations` (
  `server_url` blob NOT NULL,
  `handle` varchar(255) NOT NULL,
  `secret` blob NOT NULL,
  `issued` int(11) NOT NULL,
  `lifetime` int(11) NOT NULL,
  `assoc_type` varchar(64) NOT NULL,
  PRIMARY KEY (`server_url`(255),`handle`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `s_openid_associations`
--

LOCK TABLES `s_openid_associations` WRITE;
/*!40000 ALTER TABLE `s_openid_associations` DISABLE KEYS */;
/*!40000 ALTER TABLE `s_openid_associations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `s_openid_nonces`
--

DROP TABLE IF EXISTS `s_openid_nonces`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `s_openid_nonces` (
  `server_url` blob NOT NULL,
  `timestamp` int(11) NOT NULL,
  `salt` char(40) NOT NULL,
  PRIMARY KEY (`server_url`(255),`timestamp`,`salt`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `s_openid_nonces`
--

LOCK TABLES `s_openid_nonces` WRITE;
/*!40000 ALTER TABLE `s_openid_nonces` DISABLE KEYS */;
/*!40000 ALTER TABLE `s_openid_nonces` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2012-05-23 14:27:12
