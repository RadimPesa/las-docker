-- MySQL dump 10.13  Distrib 5.5.40, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: storage
-- ------------------------------------------------------
-- Server version	5.5.40-0ubuntu0.14.04.1

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
-- Current Database: `storage`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `storage` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `storage`;

--
-- Table structure for table `aliquot`
--

DROP TABLE IF EXISTS `aliquot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquot` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `genealogyID` varchar(30) NOT NULL,
  `idContainer` int(11) DEFAULT NULL,
  `position` varchar(10) DEFAULT NULL,
  `startTimestamp` datetime DEFAULT NULL,
  `endTimestamp` datetime DEFAULT NULL,
  `startOperator` int(11) DEFAULT NULL,
  `endOperator` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_aliquot_1` (`idContainer`),
  CONSTRAINT `fk_aliquot_1` FOREIGN KEY (`idContainer`) REFERENCES `container` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=227032 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquot`
--

LOCK TABLES `aliquot` WRITE;
/*!40000 ALTER TABLE `aliquot` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliquot` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aliquot_audit`
--

DROP TABLE IF EXISTS `aliquot_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquot_audit` (
  `id` int(11) NOT NULL,
  `genealogyID` varchar(30) NOT NULL,
  `idContainer` int(11) DEFAULT NULL,
  `position` varchar(10) DEFAULT NULL,
  `startTimestamp` datetime DEFAULT NULL,
  `endTimestamp` datetime DEFAULT NULL,
  `startOperator` int(11) DEFAULT NULL,
  `endOperator` int(11) DEFAULT NULL,
  `username` varchar(30) NOT NULL,
  `_audit_id` int(11) NOT NULL AUTO_INCREMENT,
  `_audit_timestamp` datetime NOT NULL,
  `_audit_change_type` varchar(1) NOT NULL,
  PRIMARY KEY (`_audit_id`)
) ENGINE=InnoDB AUTO_INCREMENT=228231 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquot_audit`
--

LOCK TABLES `aliquot_audit` WRITE;
/*!40000 ALTER TABLE `aliquot_audit` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliquot_audit` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE trigger audit_aliqstorage
before insert on aliquot_audit
for each row
begin
if new._audit_change_type= 'I' then
select id into @aliq_id
from aliquot
where aliquot.genealogyID= new.genealogyID and endTimestamp is null;
set new.id=@aliq_id;
END if;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `archive_member`
--

DROP TABLE IF EXISTS `archive_member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `archive_member` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `archive_member`
--

LOCK TABLES `archive_member` WRITE;
/*!40000 ALTER TABLE `archive_member` DISABLE KEYS */;
/*!40000 ALTER TABLE `archive_member` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
  KEY `auth_group_permissions_425ae3c4` (`group_id`),
  KEY `auth_group_permissions_1e014c8f` (`permission_id`),
  CONSTRAINT `group_id_refs_id_3cea63fe` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `permission_id_refs_id_5886d21f` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
  KEY `auth_permission_1bb8f392` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_728de91f` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can add group',2,'add_group'),(5,'Can change group',2,'change_group'),(6,'Can delete group',2,'delete_group'),(7,'Can add user',3,'add_user'),(8,'Can change user',3,'change_user'),(9,'Can delete user',3,'delete_user'),(10,'Can add content type',4,'add_contenttype'),(11,'Can change content type',4,'change_contenttype'),(12,'Can delete content type',4,'delete_contenttype'),(13,'Can add session',5,'add_session'),(14,'Can change session',5,'change_session'),(15,'Can delete session',5,'delete_session'),(16,'Can add site',6,'add_site'),(17,'Can change site',6,'change_site'),(18,'Can delete site',6,'delete_site'),(19,'Can add log entry',7,'add_logentry'),(20,'Can change log entry',7,'change_logentry'),(21,'Can delete log entry',7,'delete_logentry'),(22,'Can add resource',9,'add_resource'),(23,'Can change resource',9,'change_resource'),(24,'Can delete resource',9,'delete_resource'),(25,'Can add consumer',8,'add_consumer'),(26,'Can change consumer',8,'change_consumer'),(27,'Can delete consumer',8,'delete_consumer'),(28,'Can add token',10,'add_token'),(29,'Can change token',10,'change_token'),(30,'Can delete token',10,'delete_token'),(31,'Can add nonce',11,'add_nonce'),(32,'Can change nonce',11,'change_nonce'),(33,'Can delete nonce',11,'delete_nonce'),(41,'Insert New Container Type',23,'can_view_SMM_insert_new_container_type'),(42,'Insert New Container Instance',23,'can_view_SMM_insert_new_container_instance'),(43,'Change Plate Status',23,'can_view_SMM_change_plate_status'),(44,'Archive Aliquots',23,'can_view_SMM_archive_aliquots'),(45,'Move Aliquots',23,'can_view_SMM_move_aliquots'),(46,'Return Aliquots',23,'can_view_SMM_return_aliquots'),(47,'New Geometry',23,'can_view_SMM_new_geometry');
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
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
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
  KEY `auth_user_groups_403f60f` (`user_id`),
  KEY `auth_user_groups_425ae3c4` (`group_id`),
  CONSTRAINT `group_id_refs_id_f116770` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `user_id_refs_id_7ceef80f` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
  KEY `auth_user_user_permissions_403f60f` (`user_id`),
  KEY `auth_user_user_permissions_1e014c8f` (`permission_id`),
  CONSTRAINT `permission_id_refs_id_67e79cb` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `user_id_refs_id_dfbab7d` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1693 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `container`
--

DROP TABLE IF EXISTS `container`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `container` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idContainerType` int(11) NOT NULL,
  `idFatherContainer` int(11) DEFAULT NULL,
  `idGeometry` int(11) DEFAULT NULL,
  `position` varchar(10) DEFAULT NULL,
  `barcode` varchar(45) NOT NULL,
  `availability` tinyint(1) NOT NULL,
  `full` tinyint(1) NOT NULL,
  `owner` varchar(45) DEFAULT NULL,
  `present` tinyint(1) DEFAULT '1',
  `oneUse` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `barcode_UNIQUE` (`barcode`),
  KEY `fk_Container_ContainerType1` (`idContainerType`),
  KEY `fk_container_container1` (`idFatherContainer`),
  CONSTRAINT `fk_container_container1` FOREIGN KEY (`idFatherContainer`) REFERENCES `container` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_Container_ContainerType1` FOREIGN KEY (`idContainerType`) REFERENCES `containertype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=124303 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `container`
--

LOCK TABLES `container` WRITE;
/*!40000 ALTER TABLE `container` DISABLE KEYS */;
/*!40000 ALTER TABLE `container` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `container_audit`
--

DROP TABLE IF EXISTS `container_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `container_audit` (
  `id` int(11) NOT NULL,
  `idContainerType` int(11) NOT NULL,
  `idFatherContainer` int(11) DEFAULT NULL,
  `idGeometry` int(11) DEFAULT NULL,
  `position` varchar(10) DEFAULT NULL,
  `barcode` varchar(45) NOT NULL,
  `availability` tinyint(1) NOT NULL,
  `full` tinyint(1) NOT NULL,
  `owner` varchar(45) DEFAULT NULL,
  `present` tinyint(1) DEFAULT '1',
  `oneUse` tinyint(1) DEFAULT NULL,
  `username` varchar(30) NOT NULL,
  `_audit_id` int(11) NOT NULL AUTO_INCREMENT,
  `_audit_timestamp` datetime NOT NULL,
  `_audit_change_type` varchar(1) NOT NULL,
  PRIMARY KEY (`_audit_id`)
) ENGINE=InnoDB AUTO_INCREMENT=340007 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `container_audit`
--

LOCK TABLES `container_audit` WRITE;
/*!40000 ALTER TABLE `container_audit` DISABLE KEYS */;
/*!40000 ALTER TABLE `container_audit` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO' */ ;
DELIMITER ;;
CREATE TRIGGER `audit_container` BEFORE INSERT ON `container_audit` FOR EACH ROW begin
if new._audit_change_type= 'I' then
select id into @container_id
from container
where container.barcode= new.barcode;
set new.id=@container_id;
END if;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `containerfeature`
--

DROP TABLE IF EXISTS `containerfeature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `containerfeature` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idFeature` int(11) NOT NULL,
  `idContainer` int(11) NOT NULL,
  `value` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_ContainerFeature_Container1` (`idContainer`),
  KEY `fk_ContainerFeature_Feature1` (`idFeature`),
  CONSTRAINT `fk_ContainerFeature_Container1` FOREIGN KEY (`idContainer`) REFERENCES `container` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_ContainerFeature_Feature1` FOREIGN KEY (`idFeature`) REFERENCES `feature` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=170546 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `containerfeature`
--

LOCK TABLES `containerfeature` WRITE;
/*!40000 ALTER TABLE `containerfeature` DISABLE KEYS */;
/*!40000 ALTER TABLE `containerfeature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `containerinput`
--

DROP TABLE IF EXISTS `containerinput`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `containerinput` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idContainer` int(11) NOT NULL,
  `idInput` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_ContainerOutput_Container1` (`idContainer`),
  KEY `fk_ContainerInput_Input1` (`idInput`),
  CONSTRAINT `fk_ContainerInput_Input1` FOREIGN KEY (`idInput`) REFERENCES `input` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_ContainerOutput_Container10` FOREIGN KEY (`idContainer`) REFERENCES `container` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `containerinput`
--

LOCK TABLES `containerinput` WRITE;
/*!40000 ALTER TABLE `containerinput` DISABLE KEYS */;
/*!40000 ALTER TABLE `containerinput` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `containeroutput`
--

DROP TABLE IF EXISTS `containeroutput`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `containeroutput` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idOutput` int(11) NOT NULL,
  `idContainer` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_ContainerOutput_Container1` (`idContainer`),
  KEY `fk_ContainerOutput_Output1` (`idOutput`),
  CONSTRAINT `fk_ContainerOutput_Container1` FOREIGN KEY (`idContainer`) REFERENCES `container` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_ContainerOutput_Output1` FOREIGN KEY (`idOutput`) REFERENCES `output` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `containeroutput`
--

LOCK TABLES `containeroutput` WRITE;
/*!40000 ALTER TABLE `containeroutput` DISABLE KEYS */;
/*!40000 ALTER TABLE `containeroutput` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `containerrequest`
--

DROP TABLE IF EXISTS `containerrequest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `containerrequest` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idRequest` int(11) NOT NULL,
  `idContainer` int(11) NOT NULL,
  `executed` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_ContainerRequest_Container1` (`idContainer`),
  KEY `fk_ContainerRequest_Request1` (`idRequest`),
  CONSTRAINT `fk_ContainerRequest_Container1` FOREIGN KEY (`idContainer`) REFERENCES `container` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_ContainerRequest_Request1` FOREIGN KEY (`idRequest`) REFERENCES `request` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `containerrequest`
--

LOCK TABLES `containerrequest` WRITE;
/*!40000 ALTER TABLE `containerrequest` DISABLE KEYS */;
/*!40000 ALTER TABLE `containerrequest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `containertype`
--

DROP TABLE IF EXISTS `containertype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `containertype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `actualName` varchar(50) NOT NULL,
  `maxPosition` int(11) DEFAULT NULL,
  `idGenericContainerType` int(11) DEFAULT NULL,
  `idGeometry` int(11) DEFAULT NULL,
  `catalogNumber` varchar(50) DEFAULT NULL,
  `producer` varchar(50) DEFAULT NULL,
  `linkFile` varchar(100) DEFAULT NULL,
  `oneUse` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  KEY `fk_ContainerType_GenericContainerType1` (`idGenericContainerType`),
  KEY `fk_containertype_1` (`idGeometry`),
  CONSTRAINT `fk_containertype_1` FOREIGN KEY (`idGeometry`) REFERENCES `geometry` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_ContainerType_GenericContainerType1` FOREIGN KEY (`idGenericContainerType`) REFERENCES `genericcontainertype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `containertype`
--

LOCK TABLES `containertype` WRITE;
/*!40000 ALTER TABLE `containertype` DISABLE KEYS */;
INSERT INTO `containertype` VALUES (1,'Tube','Tube',1,4,2,'','','',1),(2,'FF','FF',1,4,2,'','','',1),(3,'OF','OF',1,4,2,'','','',1),(4,'CH','CH',1,4,2,'','','',1);
/*!40000 ALTER TABLE `containertype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `containertypefeature`
--

DROP TABLE IF EXISTS `containertypefeature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `containertypefeature` (
  `id` int(11) NOT NULL,
  `idFeature` int(11) NOT NULL,
  `idContainerType` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `Feature_id_UNIQUE` (`idFeature`),
  UNIQUE KEY `ContainerType_id_UNIQUE` (`idContainerType`),
  KEY `fk_ContainerType_has_Feature_Feature1` (`idFeature`),
  KEY `fk_ContainerType_has_Feature_ContainerType1` (`idContainerType`),
  CONSTRAINT `fk_ContainerType_has_Feature_ContainerType1` FOREIGN KEY (`idContainerType`) REFERENCES `containertype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_ContainerType_has_Feature_Feature1` FOREIGN KEY (`idFeature`) REFERENCES `feature` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `containertypefeature`
--

LOCK TABLES `containertypefeature` WRITE;
/*!40000 ALTER TABLE `containertypefeature` DISABLE KEYS */;
/*!40000 ALTER TABLE `containertypefeature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `conttypehasconttype`
--

DROP TABLE IF EXISTS `conttypehasconttype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `conttypehasconttype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idContainer` int(11) DEFAULT NULL,
  `idContained` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_conttypehasconttype_containerType1` (`idContainer`),
  KEY `fk_conttypehasconttype_containerType2` (`idContained`),
  CONSTRAINT `fk_conttypehasconttype_containerType1` FOREIGN KEY (`idContainer`) REFERENCES `containertype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_conttypehasconttype_containerType2` FOREIGN KEY (`idContained`) REFERENCES `containertype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conttypehasconttype`
--

LOCK TABLES `conttypehasconttype` WRITE;
/*!40000 ALTER TABLE `conttypehasconttype` DISABLE KEYS */;
INSERT INTO `conttypehasconttype` VALUES (1,1,NULL),(2,2,NULL),(3,3,NULL),(4,4,NULL);
/*!40000 ALTER TABLE `conttypehasconttype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary table structure for view `currentaliquot`
--

DROP TABLE IF EXISTS `currentaliquot`;
/*!50001 DROP VIEW IF EXISTS `currentaliquot`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `currentaliquot` (
  `id` tinyint NOT NULL,
  `genealogyID` tinyint NOT NULL,
  `idContainer` tinyint NOT NULL,
  `position` tinyint NOT NULL,
  `startTimestamp` tinyint NOT NULL,
  `endTimestamp` tinyint NOT NULL,
  `startOperator` tinyint NOT NULL,
  `endOperator` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `defaultvalue`
--

DROP TABLE IF EXISTS `defaultvalue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `defaultvalue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `longName` varchar(20) NOT NULL,
  `abbreviation` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `defaultvalue`
--

LOCK TABLES `defaultvalue` WRITE;
/*!40000 ALTER TABLE `defaultvalue` DISABLE KEYS */;
INSERT INTO `defaultvalue` VALUES (1,'Viable','VT'),(2,'Snap frozen','SF'),(3,'RNAlater','RL'),(4,'Formalin Fixed','FF'),(5,'OCTfrozen','OF'),(6,'ChinaBlack','CH'),(7,'DNA','DNA'),(8,'RNA','RNA'),(9,'Complementary DNA','cDNA'),(10,'Complementary RNA','cRNA'),(11,'Operative',NULL),(12,'Stored',NULL),(13,'Transient',NULL),(14,'Extern',NULL),(15,'Plasma','PL'),(16,'PAXtube','PX'),(17,'Frozen','FR'),(18,'FrozenSediment','FS'),(19,'ParaffinSection','PS'),(20,'OCTSection','OS'),(21,'Protein','P');
/*!40000 ALTER TABLE `defaultvalue` ENABLE KEYS */;
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
  KEY `django_admin_log_403f60f` (`user_id`),
  KEY `django_admin_log_1bb8f392` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_288599e6` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `user_id_refs_id_c8665aa` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1750 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'permission','auth','permission'),(2,'group','auth','group'),(3,'user','auth','user'),(4,'content type','contenttypes','contenttype'),(5,'session','sessions','session'),(6,'site','sites','site'),(7,'log entry','admin','logentry'),(8,'consumer','piston','consumer'),(9,'resource','piston','resource'),(10,'token','piston','token'),(11,'nonce','piston','nonce'),(12,'container','archive','container'),(13,'urls','archive','urls'),(14,'feature default value','archive','featuredefaultvalue'),(15,'default values','archive','defaultvalues'),(16,'container feature','archive','containerfeature'),(17,'feature','archive','feature'),(18,'container type','archive','containertype'),(19,'cont type has cont type','archive','conttypehasconttype'),(20,'geometry','archive','geometry'),(21,'default value','archive','defaultvalue'),(22,'generic container type','archive','genericcontainertype'),(23,'member','archive','member'),(24,'aliquot','archive','aliquot');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
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
  KEY `django_session_3da3d3d8` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES (1,'https://lastest.polito.it','LASDomain');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feature`
--

DROP TABLE IF EXISTS `feature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `feature` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feature`
--

LOCK TABLES `feature` WRITE;
/*!40000 ALTER TABLE `feature` DISABLE KEYS */;
INSERT INTO `feature` VALUES (1,'AliquotType'),(2,'PlateAim');
/*!40000 ALTER TABLE `feature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `featuredefaultvalue`
--

DROP TABLE IF EXISTS `featuredefaultvalue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `featuredefaultvalue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idFeature` int(11) NOT NULL,
  `idDefaultValue` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_featureDefaultValue_feature1` (`idFeature`),
  KEY `fk_featureDefaultValue_defaultValue1` (`idDefaultValue`),
  CONSTRAINT `fk_featureDefaultValue_defaultValue1` FOREIGN KEY (`idDefaultValue`) REFERENCES `defaultvalue` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_featureDefaultValue_feature1` FOREIGN KEY (`idFeature`) REFERENCES `feature` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `featuredefaultvalue`
--

LOCK TABLES `featuredefaultvalue` WRITE;
/*!40000 ALTER TABLE `featuredefaultvalue` DISABLE KEYS */;
INSERT INTO `featuredefaultvalue` VALUES (1,1,1),(2,1,2),(3,1,3),(4,1,7),(5,1,8),(6,1,9),(7,1,10),(8,2,11),(9,2,12),(10,2,13),(11,2,14),(12,1,15),(13,1,16),(14,1,17),(15,1,18),(19,1,19),(20,1,20),(21,1,21);
/*!40000 ALTER TABLE `featuredefaultvalue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genericcontainertype`
--

DROP TABLE IF EXISTS `genericcontainertype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `genericcontainertype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `abbreviation` varchar(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genericcontainertype`
--

LOCK TABLES `genericcontainertype` WRITE;
/*!40000 ALTER TABLE `genericcontainertype` DISABLE KEYS */;
INSERT INTO `genericcontainertype` VALUES (1,'Freezer/Cabinet','freezer'),(2,'Rack/Drawer','rack'),(3,'Plate/Box','plate'),(4,'Tube/BioCassette','tube');
/*!40000 ALTER TABLE `genericcontainertype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geometry`
--

DROP TABLE IF EXISTS `geometry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `geometry` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `rules` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geometry`
--

LOCK TABLES `geometry` WRITE;
/*!40000 ALTER TABLE `geometry` DISABLE KEYS */;
INSERT INTO `geometry` VALUES (2,'1x1','{\r\n    \"dimension\": [1, 1], \r\n   \"row_label\": [\"A\"],\"column_label\": [1],\"items\": [{\"id\":\"A1\",\"position\":[1,1]}]\r\n}\r\n'),(4,'28x4','{\"dimension\": [4,28],\"row_label\": [\"AA\",\"AB\",\"AC\",\"AD\",\"AE\",\"AF\",\"AG\",\"AH\",\"AI\",\"AJ\",\"AK\",\"AL\",\"AM\",\"AN\",\"BA\",\"BB\",\"BC\",\"BD\",\"BE\",\"BF\",\"BG\",\"BH\",\"BI\",\"BJ\",\"BK\",\"BL\",\"BM\",\"BN\"],\"column_label\": [1,2,3,4],\"items\": [{\"id\":\"AA1\",\"position\":[1,1]},{\"id\":\"AA2\",\"position\":[2,1]},{\"id\":\"AA3\",\"position\":[3,1]},{\"id\":\"AA4\",\"position\":[4,1]},{\"id\":\"AB1\",\"position\":[1,2]},{\"id\":\"AB2\",\"position\":[2,2]},{\"id\":\"AB3\",\"position\":[3,2]},{\"id\":\"AB4\",\"position\":[4,2]},{\"id\":\"AC1\",\"position\":[1,3]},{\"id\":\"AC2\",\"position\":[2,3]},{\"id\":\"AC3\",\"position\":[3,3]},{\"id\":\"AC4\",\"position\":[4,3]},{\"id\":\"AD1\",\"position\":[1,4]},{\"id\":\"AD2\",\"position\":[2,4]},{\"id\":\"AD3\",\"position\":[3,4]},{\"id\":\"AD4\",\"position\":[4,4]},{\"id\":\"AE1\",\"position\":[1,5]},{\"id\":\"AE2\",\"position\":[2,5]},{\"id\":\"AE3\",\"position\":[3,5]},{\"id\":\"AE4\",\"position\":[4,5]},{\"id\":\"AF1\",\"position\":[1,6]},{\"id\":\"AF2\",\"position\":[2,6]},{\"id\":\"AF3\",\"position\":[3,6]},{\"id\":\"AF4\",\"position\":[4,6]},{\"id\":\"AG1\",\"position\":[1,7]},{\"id\":\"AG2\",\"position\":[2,7]},{\"id\":\"AG3\",\"position\":[3,7]},{\"id\":\"AG4\",\"position\":[4,7]},{\"id\":\"AH1\",\"position\":[1,8]},{\"id\":\"AH2\",\"position\":[2,8]},{\"id\":\"AH3\",\"position\":[3,8]},{\"id\":\"AH4\",\"position\":[4,8]},{\"id\":\"AI1\",\"position\":[1,9]},{\"id\":\"AI2\",\"position\":[2,9]},{\"id\":\"AI3\",\"position\":[3,9]},{\"id\":\"AI4\",\"position\":[4,9]},{\"id\":\"AJ1\",\"position\":[1,10]},{\"id\":\"AJ2\",\"position\":[2,10]},{\"id\":\"AJ3\",\"position\":[3,10]},{\"id\":\"AJ4\",\"position\":[4,10]},{\"id\":\"AK1\",\"position\":[1,11]},{\"id\":\"AK2\",\"position\":[2,11]},{\"id\":\"AK3\",\"position\":[3,11]},{\"id\":\"AK4\",\"position\":[4,11]},{\"id\":\"AL1\",\"position\":[1,12]},{\"id\":\"AL2\",\"position\":[2,12]},{\"id\":\"AL3\",\"position\":[3,12]},{\"id\":\"AL4\",\"position\":[4,12]},{\"id\":\"AM1\",\"position\":[1,13]},{\"id\":\"AM2\",\"position\":[2,13]},{\"id\":\"AM3\",\"position\":[3,13]},{\"id\":\"AM4\",\"position\":[4,13]},{\"id\":\"AN1\",\"position\":[1,14]},{\"id\":\"AN2\",\"position\":[2,14]},{\"id\":\"AN3\",\"position\":[3,14]},{\"id\":\"AN4\",\"position\":[4,14]},{\"id\":\"BA1\",\"position\":[1,15]},{\"id\":\"BA2\",\"position\":[2,15]},{\"id\":\"BA3\",\"position\":[3,15]},{\"id\":\"BA4\",\"position\":[4,15]},{\"id\":\"BB1\",\"position\":[1,16]},{\"id\":\"BB2\",\"position\":[2,16]},{\"id\":\"BB3\",\"position\":[3,16]},{\"id\":\"BB4\",\"position\":[4,16]},{\"id\":\"BC1\",\"position\":[1,17]},{\"id\":\"BC2\",\"position\":[2,17]},{\"id\":\"BC3\",\"position\":[3,17]},{\"id\":\"BC4\",\"position\":[4,17]},{\"id\":\"BD1\",\"position\":[1,18]},{\"id\":\"BD2\",\"position\":[2,18]},{\"id\":\"BD3\",\"position\":[3,18]},{\"id\":\"BD4\",\"position\":[4,18]},{\"id\":\"BE1\",\"position\":[1,19]},{\"id\":\"BE2\",\"position\":[2,19]},{\"id\":\"BE3\",\"position\":[3,19]},{\"id\":\"BE4\",\"position\":[4,19]},{\"id\":\"BF1\",\"position\":[1,20]},{\"id\":\"BF2\",\"position\":[2,20]},{\"id\":\"BF3\",\"position\":[3,20]},{\"id\":\"BF4\",\"position\":[4,20]},{\"id\":\"BG1\",\"position\":[1,21]},{\"id\":\"BG2\",\"position\":[2,21]},{\"id\":\"BG3\",\"position\":[3,21]},{\"id\":\"BG4\",\"position\":[4,21]},{\"id\":\"BH1\",\"position\":[1,22]},{\"id\":\"BH2\",\"position\":[2,22]},{\"id\":\"BH3\",\"position\":[3,22]},{\"id\":\"BH4\",\"position\":[4,22]},{\"id\":\"BI1\",\"position\":[1,23]},{\"id\":\"BI2\",\"position\":[2,23]},{\"id\":\"BI3\",\"position\":[3,23]},{\"id\":\"BI4\",\"position\":[4,23]},{\"id\":\"BJ1\",\"position\":[1,24]},{\"id\":\"BJ2\",\"position\":[2,24]},{\"id\":\"BJ3\",\"position\":[3,24]},{\"id\":\"BJ4\",\"position\":[4,24]},{\"id\":\"BK1\",\"position\":[1,25]},{\"id\":\"BK2\",\"position\":[2,25]},{\"id\":\"BK3\",\"position\":[3,25]},{\"id\":\"BK4\",\"position\":[4,25]},{\"id\":\"BL1\",\"position\":[1,26]},{\"id\":\"BL2\",\"position\":[2,26]},{\"id\":\"BL3\",\"position\":[3,26]},{\"id\":\"BL4\",\"position\":[4,26]},{\"id\":\"BM1\",\"position\":[1,27]},{\"id\":\"BM2\",\"position\":[2,27]},{\"id\":\"BM3\",\"position\":[3,27]},{\"id\":\"BM4\",\"position\":[4,27]},{\"id\":\"BN1\",\"position\":[1,28]},{\"id\":\"BN2\",\"position\":[2,28]},{\"id\":\"BN3\",\"position\":[3,28]},{\"id\":\"BN4\",\"position\":[4,28]}]}'),(13,'8x12','{\"dimension\": [12,8],\"row_label\": [\"A\",\"B\",\"C\",\"D\",\"E\",\"F\",\"G\",\"H\"],\"column_label\": [1,2,3,4,5,6,7,8,9,10,11,12],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"A5\",\"position\":[5,1]},{\"id\":\"A6\",\"position\":[6,1]},{\"id\":\"A7\",\"position\":[7,1]},{\"id\":\"A8\",\"position\":[8,1]},{\"id\":\"A9\",\"position\":[9,1]},{\"id\":\"A10\",\"position\":[10,1]},{\"id\":\"A11\",\"position\":[11,1]},{\"id\":\"A12\",\"position\":[12,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]},{\"id\":\"B4\",\"position\":[4,2]},{\"id\":\"B5\",\"position\":[5,2]},{\"id\":\"B6\",\"position\":[6,2]},{\"id\":\"B7\",\"position\":[7,2]},{\"id\":\"B8\",\"position\":[8,2]},{\"id\":\"B9\",\"position\":[9,2]},{\"id\":\"B10\",\"position\":[10,2]},{\"id\":\"B11\",\"position\":[11,2]},{\"id\":\"B12\",\"position\":[12,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"C2\",\"position\":[2,3]},{\"id\":\"C3\",\"position\":[3,3]},{\"id\":\"C4\",\"position\":[4,3]},{\"id\":\"C5\",\"position\":[5,3]},{\"id\":\"C6\",\"position\":[6,3]},{\"id\":\"C7\",\"position\":[7,3]},{\"id\":\"C8\",\"position\":[8,3]},{\"id\":\"C9\",\"position\":[9,3]},{\"id\":\"C10\",\"position\":[10,3]},{\"id\":\"C11\",\"position\":[11,3]},{\"id\":\"C12\",\"position\":[12,3]},{\"id\":\"D1\",\"position\":[1,4]},{\"id\":\"D2\",\"position\":[2,4]},{\"id\":\"D3\",\"position\":[3,4]},{\"id\":\"D4\",\"position\":[4,4]},{\"id\":\"D5\",\"position\":[5,4]},{\"id\":\"D6\",\"position\":[6,4]},{\"id\":\"D7\",\"position\":[7,4]},{\"id\":\"D8\",\"position\":[8,4]},{\"id\":\"D9\",\"position\":[9,4]},{\"id\":\"D10\",\"position\":[10,4]},{\"id\":\"D11\",\"position\":[11,4]},{\"id\":\"D12\",\"position\":[12,4]},{\"id\":\"E1\",\"position\":[1,5]},{\"id\":\"E2\",\"position\":[2,5]},{\"id\":\"E3\",\"position\":[3,5]},{\"id\":\"E4\",\"position\":[4,5]},{\"id\":\"E5\",\"position\":[5,5]},{\"id\":\"E6\",\"position\":[6,5]},{\"id\":\"E7\",\"position\":[7,5]},{\"id\":\"E8\",\"position\":[8,5]},{\"id\":\"E9\",\"position\":[9,5]},{\"id\":\"E10\",\"position\":[10,5]},{\"id\":\"E11\",\"position\":[11,5]},{\"id\":\"E12\",\"position\":[12,5]},{\"id\":\"F1\",\"position\":[1,6]},{\"id\":\"F2\",\"position\":[2,6]},{\"id\":\"F3\",\"position\":[3,6]},{\"id\":\"F4\",\"position\":[4,6]},{\"id\":\"F5\",\"position\":[5,6]},{\"id\":\"F6\",\"position\":[6,6]},{\"id\":\"F7\",\"position\":[7,6]},{\"id\":\"F8\",\"position\":[8,6]},{\"id\":\"F9\",\"position\":[9,6]},{\"id\":\"F10\",\"position\":[10,6]},{\"id\":\"F11\",\"position\":[11,6]},{\"id\":\"F12\",\"position\":[12,6]},{\"id\":\"G1\",\"position\":[1,7]},{\"id\":\"G2\",\"position\":[2,7]},{\"id\":\"G3\",\"position\":[3,7]},{\"id\":\"G4\",\"position\":[4,7]},{\"id\":\"G5\",\"position\":[5,7]},{\"id\":\"G6\",\"position\":[6,7]},{\"id\":\"G7\",\"position\":[7,7]},{\"id\":\"G8\",\"position\":[8,7]},{\"id\":\"G9\",\"position\":[9,7]},{\"id\":\"G10\",\"position\":[10,7]},{\"id\":\"G11\",\"position\":[11,7]},{\"id\":\"G12\",\"position\":[12,7]},{\"id\":\"H1\",\"position\":[1,8]},{\"id\":\"H2\",\"position\":[2,8]},{\"id\":\"H3\",\"position\":[3,8]},{\"id\":\"H4\",\"position\":[4,8]},{\"id\":\"H5\",\"position\":[5,8]},{\"id\":\"H6\",\"position\":[6,8]},{\"id\":\"H7\",\"position\":[7,8]},{\"id\":\"H8\",\"position\":[8,8]},{\"id\":\"H9\",\"position\":[9,8]},{\"id\":\"H10\",\"position\":[10,8]},{\"id\":\"H11\",\"position\":[11,8]},{\"id\":\"H12\",\"position\":[12,8]}]}'),(14,'4x6','{\"dimension\": [6,4],\"row_label\": [\"A\",\"B\",\"C\",\"D\"],\"column_label\": [1,2,3,4,5,6],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"A5\",\"position\":[5,1]},{\"id\":\"A6\",\"position\":[6,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]},{\"id\":\"B4\",\"position\":[4,2]},{\"id\":\"B5\",\"position\":[5,2]},{\"id\":\"B6\",\"position\":[6,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"C2\",\"position\":[2,3]},{\"id\":\"C3\",\"position\":[3,3]},{\"id\":\"C4\",\"position\":[4,3]},{\"id\":\"C5\",\"position\":[5,3]},{\"id\":\"C6\",\"position\":[6,3]},{\"id\":\"D1\",\"position\":[1,4]},{\"id\":\"D2\",\"position\":[2,4]},{\"id\":\"D3\",\"position\":[3,4]},{\"id\":\"D4\",\"position\":[4,4]},{\"id\":\"D5\",\"position\":[5,4]},{\"id\":\"D6\",\"position\":[6,4]}]}'),(15,'2x3','{\"dimension\": [3,2],\"row_label\": [\"A\",\"B\"],\"column_label\": [1,2,3],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]}]}'),(17,'9x9','{\"dimension\": [9,9],\"row_label\": [\"A\",\"B\",\"C\",\"D\",\"E\",\"F\",\"G\",\"H\",\"I\"],\"column_label\": [1,2,3,4,5,6,7,8,9],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"A5\",\"position\":[5,1]},{\"id\":\"A6\",\"position\":[6,1]},{\"id\":\"A7\",\"position\":[7,1]},{\"id\":\"A8\",\"position\":[8,1]},{\"id\":\"A9\",\"position\":[9,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]},{\"id\":\"B4\",\"position\":[4,2]},{\"id\":\"B5\",\"position\":[5,2]},{\"id\":\"B6\",\"position\":[6,2]},{\"id\":\"B7\",\"position\":[7,2]},{\"id\":\"B8\",\"position\":[8,2]},{\"id\":\"B9\",\"position\":[9,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"C2\",\"position\":[2,3]},{\"id\":\"C3\",\"position\":[3,3]},{\"id\":\"C4\",\"position\":[4,3]},{\"id\":\"C5\",\"position\":[5,3]},{\"id\":\"C6\",\"position\":[6,3]},{\"id\":\"C7\",\"position\":[7,3]},{\"id\":\"C8\",\"position\":[8,3]},{\"id\":\"C9\",\"position\":[9,3]},{\"id\":\"D1\",\"position\":[1,4]},{\"id\":\"D2\",\"position\":[2,4]},{\"id\":\"D3\",\"position\":[3,4]},{\"id\":\"D4\",\"position\":[4,4]},{\"id\":\"D5\",\"position\":[5,4]},{\"id\":\"D6\",\"position\":[6,4]},{\"id\":\"D7\",\"position\":[7,4]},{\"id\":\"D8\",\"position\":[8,4]},{\"id\":\"D9\",\"position\":[9,4]},{\"id\":\"E1\",\"position\":[1,5]},{\"id\":\"E2\",\"position\":[2,5]},{\"id\":\"E3\",\"position\":[3,5]},{\"id\":\"E4\",\"position\":[4,5]},{\"id\":\"E5\",\"position\":[5,5]},{\"id\":\"E6\",\"position\":[6,5]},{\"id\":\"E7\",\"position\":[7,5]},{\"id\":\"E8\",\"position\":[8,5]},{\"id\":\"E9\",\"position\":[9,5]},{\"id\":\"F1\",\"position\":[1,6]},{\"id\":\"F2\",\"position\":[2,6]},{\"id\":\"F3\",\"position\":[3,6]},{\"id\":\"F4\",\"position\":[4,6]},{\"id\":\"F5\",\"position\":[5,6]},{\"id\":\"F6\",\"position\":[6,6]},{\"id\":\"F7\",\"position\":[7,6]},{\"id\":\"F8\",\"position\":[8,6]},{\"id\":\"F9\",\"position\":[9,6]},{\"id\":\"G1\",\"position\":[1,7]},{\"id\":\"G2\",\"position\":[2,7]},{\"id\":\"G3\",\"position\":[3,7]},{\"id\":\"G4\",\"position\":[4,7]},{\"id\":\"G5\",\"position\":[5,7]},{\"id\":\"G6\",\"position\":[6,7]},{\"id\":\"G7\",\"position\":[7,7]},{\"id\":\"G8\",\"position\":[8,7]},{\"id\":\"G9\",\"position\":[9,7]},{\"id\":\"H1\",\"position\":[1,8]},{\"id\":\"H2\",\"position\":[2,8]},{\"id\":\"H3\",\"position\":[3,8]},{\"id\":\"H4\",\"position\":[4,8]},{\"id\":\"H5\",\"position\":[5,8]},{\"id\":\"H6\",\"position\":[6,8]},{\"id\":\"H7\",\"position\":[7,8]},{\"id\":\"H8\",\"position\":[8,8]},{\"id\":\"H9\",\"position\":[9,8]},{\"id\":\"I1\",\"position\":[1,9]},{\"id\":\"I2\",\"position\":[2,9]},{\"id\":\"I3\",\"position\":[3,9]},{\"id\":\"I4\",\"position\":[4,9]},{\"id\":\"I5\",\"position\":[5,9]},{\"id\":\"I6\",\"position\":[6,9]},{\"id\":\"I7\",\"position\":[7,9]},{\"id\":\"I8\",\"position\":[8,9]},{\"id\":\"I9\",\"position\":[9,9]}]}'),(18,'4x4','{\"dimension\": [4,4],\"row_label\": [\"A\",\"B\",\"C\",\"D\"],\"column_label\": [1,2,3,4],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]},{\"id\":\"B4\",\"position\":[4,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"C2\",\"position\":[2,3]},{\"id\":\"C3\",\"position\":[3,3]},{\"id\":\"C4\",\"position\":[4,3]},{\"id\":\"D1\",\"position\":[1,4]},{\"id\":\"D2\",\"position\":[2,4]},{\"id\":\"D3\",\"position\":[3,4]},{\"id\":\"D4\",\"position\":[4,4]}]}'),(19,'4x3','{\"dimension\": [3,4],\"row_label\": [\"A\",\"B\",\"C\",\"D\"],\"column_label\": [1,2,3],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"C2\",\"position\":[2,3]},{\"id\":\"C3\",\"position\":[3,3]},{\"id\":\"D1\",\"position\":[1,4]},{\"id\":\"D2\",\"position\":[2,4]},{\"id\":\"D3\",\"position\":[3,4]}]}'),(20,'12x1','{\"dimension\": [1,12],\"row_label\": [\"A\",\"B\",\"C\",\"D\",\"E\",\"F\",\"G\",\"H\",\"I\",\"J\",\"K\",\"L\"],\"column_label\": [1],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"D1\",\"position\":[1,4]},{\"id\":\"E1\",\"position\":[1,5]},{\"id\":\"F1\",\"position\":[1,6]},{\"id\":\"G1\",\"position\":[1,7]},{\"id\":\"H1\",\"position\":[1,8]},{\"id\":\"I1\",\"position\":[1,9]},{\"id\":\"J1\",\"position\":[1,10]},{\"id\":\"K1\",\"position\":[1,11]},{\"id\":\"L1\",\"position\":[1,12]}]}'),(21,'3x3','{\"dimension\": [3,3],\"row_label\": [\"A\",\"B\",\"C\"],\"column_label\": [1,2,3],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"C2\",\"position\":[2,3]},{\"id\":\"C3\",\"position\":[3,3]}]}'),(23,'10x10','{\"dimension\": [10,10],\"row_label\": [\"A\",\"B\",\"C\",\"D\",\"E\",\"F\",\"G\",\"H\",\"I\",\"J\"],\"column_label\": [1,2,3,4,5,6,7,8,9,10],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"A5\",\"position\":[5,1]},{\"id\":\"A6\",\"position\":[6,1]},{\"id\":\"A7\",\"position\":[7,1]},{\"id\":\"A8\",\"position\":[8,1]},{\"id\":\"A9\",\"position\":[9,1]},{\"id\":\"A10\",\"position\":[10,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]},{\"id\":\"B4\",\"position\":[4,2]},{\"id\":\"B5\",\"position\":[5,2]},{\"id\":\"B6\",\"position\":[6,2]},{\"id\":\"B7\",\"position\":[7,2]},{\"id\":\"B8\",\"position\":[8,2]},{\"id\":\"B9\",\"position\":[9,2]},{\"id\":\"B10\",\"position\":[10,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"C2\",\"position\":[2,3]},{\"id\":\"C3\",\"position\":[3,3]},{\"id\":\"C4\",\"position\":[4,3]},{\"id\":\"C5\",\"position\":[5,3]},{\"id\":\"C6\",\"position\":[6,3]},{\"id\":\"C7\",\"position\":[7,3]},{\"id\":\"C8\",\"position\":[8,3]},{\"id\":\"C9\",\"position\":[9,3]},{\"id\":\"C10\",\"position\":[10,3]},{\"id\":\"D1\",\"position\":[1,4]},{\"id\":\"D2\",\"position\":[2,4]},{\"id\":\"D3\",\"position\":[3,4]},{\"id\":\"D4\",\"position\":[4,4]},{\"id\":\"D5\",\"position\":[5,4]},{\"id\":\"D6\",\"position\":[6,4]},{\"id\":\"D7\",\"position\":[7,4]},{\"id\":\"D8\",\"position\":[8,4]},{\"id\":\"D9\",\"position\":[9,4]},{\"id\":\"D10\",\"position\":[10,4]},{\"id\":\"E1\",\"position\":[1,5]},{\"id\":\"E2\",\"position\":[2,5]},{\"id\":\"E3\",\"position\":[3,5]},{\"id\":\"E4\",\"position\":[4,5]},{\"id\":\"E5\",\"position\":[5,5]},{\"id\":\"E6\",\"position\":[6,5]},{\"id\":\"E7\",\"position\":[7,5]},{\"id\":\"E8\",\"position\":[8,5]},{\"id\":\"E9\",\"position\":[9,5]},{\"id\":\"E10\",\"position\":[10,5]},{\"id\":\"F1\",\"position\":[1,6]},{\"id\":\"F2\",\"position\":[2,6]},{\"id\":\"F3\",\"position\":[3,6]},{\"id\":\"F4\",\"position\":[4,6]},{\"id\":\"F5\",\"position\":[5,6]},{\"id\":\"F6\",\"position\":[6,6]},{\"id\":\"F7\",\"position\":[7,6]},{\"id\":\"F8\",\"position\":[8,6]},{\"id\":\"F9\",\"position\":[9,6]},{\"id\":\"F10\",\"position\":[10,6]},{\"id\":\"G1\",\"position\":[1,7]},{\"id\":\"G2\",\"position\":[2,7]},{\"id\":\"G3\",\"position\":[3,7]},{\"id\":\"G4\",\"position\":[4,7]},{\"id\":\"G5\",\"position\":[5,7]},{\"id\":\"G6\",\"position\":[6,7]},{\"id\":\"G7\",\"position\":[7,7]},{\"id\":\"G8\",\"position\":[8,7]},{\"id\":\"G9\",\"position\":[9,7]},{\"id\":\"G10\",\"position\":[10,7]},{\"id\":\"H1\",\"position\":[1,8]},{\"id\":\"H2\",\"position\":[2,8]},{\"id\":\"H3\",\"position\":[3,8]},{\"id\":\"H4\",\"position\":[4,8]},{\"id\":\"H5\",\"position\":[5,8]},{\"id\":\"H6\",\"position\":[6,8]},{\"id\":\"H7\",\"position\":[7,8]},{\"id\":\"H8\",\"position\":[8,8]},{\"id\":\"H9\",\"position\":[9,8]},{\"id\":\"H10\",\"position\":[10,8]},{\"id\":\"I1\",\"position\":[1,9]},{\"id\":\"I2\",\"position\":[2,9]},{\"id\":\"I3\",\"position\":[3,9]},{\"id\":\"I4\",\"position\":[4,9]},{\"id\":\"I5\",\"position\":[5,9]},{\"id\":\"I6\",\"position\":[6,9]},{\"id\":\"I7\",\"position\":[7,9]},{\"id\":\"I8\",\"position\":[8,9]},{\"id\":\"I9\",\"position\":[9,9]},{\"id\":\"I10\",\"position\":[10,9]},{\"id\":\"J1\",\"position\":[1,10]},{\"id\":\"J2\",\"position\":[2,10]},{\"id\":\"J3\",\"position\":[3,10]},{\"id\":\"J4\",\"position\":[4,10]},{\"id\":\"J5\",\"position\":[5,10]},{\"id\":\"J6\",\"position\":[6,10]},{\"id\":\"J7\",\"position\":[7,10]},{\"id\":\"J8\",\"position\":[8,10]},{\"id\":\"J9\",\"position\":[9,10]},{\"id\":\"J10\",\"position\":[10,10]}]}'),(24,'3x4','{\"dimension\": [4,3],\"row_label\": [\"A\",\"B\",\"C\"],\"column_label\": [1,2,3,4],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]},{\"id\":\"B4\",\"position\":[4,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"C2\",\"position\":[2,3]},{\"id\":\"C3\",\"position\":[3,3]},{\"id\":\"C4\",\"position\":[4,3]}]}'),(25,'5x5','{\"dimension\": [5,5],\"row_label\": [\"A\",\"B\",\"C\",\"D\",\"E\"],\"column_label\": [1,2,3,4,5],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"A5\",\"position\":[5,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]},{\"id\":\"B4\",\"position\":[4,2]},{\"id\":\"B5\",\"position\":[5,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"C2\",\"position\":[2,3]},{\"id\":\"C3\",\"position\":[3,3]},{\"id\":\"C4\",\"position\":[4,3]},{\"id\":\"C5\",\"position\":[5,3]},{\"id\":\"D1\",\"position\":[1,4]},{\"id\":\"D2\",\"position\":[2,4]},{\"id\":\"D3\",\"position\":[3,4]},{\"id\":\"D4\",\"position\":[4,4]},{\"id\":\"D5\",\"position\":[5,4]},{\"id\":\"E1\",\"position\":[1,5]},{\"id\":\"E2\",\"position\":[2,5]},{\"id\":\"E3\",\"position\":[3,5]},{\"id\":\"E4\",\"position\":[4,5]},{\"id\":\"E5\",\"position\":[5,5]}]}'),(26,'4x14','{\"dimension\": [14,4],\"row_label\": [\"A\",\"B\",\"C\",\"D\"],\"column_label\": [1,2,3,4,5,6,7,8,9,10,11,12,13,14],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"A5\",\"position\":[5,1]},{\"id\":\"A6\",\"position\":[6,1]},{\"id\":\"A7\",\"position\":[7,1]},{\"id\":\"A8\",\"position\":[8,1]},{\"id\":\"A9\",\"position\":[9,1]},{\"id\":\"A10\",\"position\":[10,1]},{\"id\":\"A11\",\"position\":[11,1]},{\"id\":\"A12\",\"position\":[12,1]},{\"id\":\"A13\",\"position\":[13,1]},{\"id\":\"A14\",\"position\":[14,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]},{\"id\":\"B4\",\"position\":[4,2]},{\"id\":\"B5\",\"position\":[5,2]},{\"id\":\"B6\",\"position\":[6,2]},{\"id\":\"B7\",\"position\":[7,2]},{\"id\":\"B8\",\"position\":[8,2]},{\"id\":\"B9\",\"position\":[9,2]},{\"id\":\"B10\",\"position\":[10,2]},{\"id\":\"B11\",\"position\":[11,2]},{\"id\":\"B12\",\"position\":[12,2]},{\"id\":\"B13\",\"position\":[13,2]},{\"id\":\"B14\",\"position\":[14,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"C2\",\"position\":[2,3]},{\"id\":\"C3\",\"position\":[3,3]},{\"id\":\"C4\",\"position\":[4,3]},{\"id\":\"C5\",\"position\":[5,3]},{\"id\":\"C6\",\"position\":[6,3]},{\"id\":\"C7\",\"position\":[7,3]},{\"id\":\"C8\",\"position\":[8,3]},{\"id\":\"C9\",\"position\":[9,3]},{\"id\":\"C10\",\"position\":[10,3]},{\"id\":\"C11\",\"position\":[11,3]},{\"id\":\"C12\",\"position\":[12,3]},{\"id\":\"C13\",\"position\":[13,3]},{\"id\":\"C14\",\"position\":[14,3]},{\"id\":\"D1\",\"position\":[1,4]},{\"id\":\"D2\",\"position\":[2,4]},{\"id\":\"D3\",\"position\":[3,4]},{\"id\":\"D4\",\"position\":[4,4]},{\"id\":\"D5\",\"position\":[5,4]},{\"id\":\"D6\",\"position\":[6,4]},{\"id\":\"D7\",\"position\":[7,4]},{\"id\":\"D8\",\"position\":[8,4]},{\"id\":\"D9\",\"position\":[9,4]},{\"id\":\"D10\",\"position\":[10,4]},{\"id\":\"D11\",\"position\":[11,4]},{\"id\":\"D12\",\"position\":[12,4]},{\"id\":\"D13\",\"position\":[13,4]},{\"id\":\"D14\",\"position\":[14,4]}]}'),(27,'1x6','{\"dimension\": [6,1],\"row_label\": [\"A\"],\"column_label\": [1,2,3,4,5,6],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"A5\",\"position\":[5,1]},{\"id\":\"A6\",\"position\":[6,1]}]}'),(28,'1x100','{\"dimension\": [100,1],\"row_label\": [\"A\"],\"column_label\": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"A5\",\"position\":[5,1]},{\"id\":\"A6\",\"position\":[6,1]},{\"id\":\"A7\",\"position\":[7,1]},{\"id\":\"A8\",\"position\":[8,1]},{\"id\":\"A9\",\"position\":[9,1]},{\"id\":\"A10\",\"position\":[10,1]},{\"id\":\"A11\",\"position\":[11,1]},{\"id\":\"A12\",\"position\":[12,1]},{\"id\":\"A13\",\"position\":[13,1]},{\"id\":\"A14\",\"position\":[14,1]},{\"id\":\"A15\",\"position\":[15,1]},{\"id\":\"A16\",\"position\":[16,1]},{\"id\":\"A17\",\"position\":[17,1]},{\"id\":\"A18\",\"position\":[18,1]},{\"id\":\"A19\",\"position\":[19,1]},{\"id\":\"A20\",\"position\":[20,1]},{\"id\":\"A21\",\"position\":[21,1]},{\"id\":\"A22\",\"position\":[22,1]},{\"id\":\"A23\",\"position\":[23,1]},{\"id\":\"A24\",\"position\":[24,1]},{\"id\":\"A25\",\"position\":[25,1]},{\"id\":\"A26\",\"position\":[26,1]},{\"id\":\"A27\",\"position\":[27,1]},{\"id\":\"A28\",\"position\":[28,1]},{\"id\":\"A29\",\"position\":[29,1]},{\"id\":\"A30\",\"position\":[30,1]},{\"id\":\"A31\",\"position\":[31,1]},{\"id\":\"A32\",\"position\":[32,1]},{\"id\":\"A33\",\"position\":[33,1]},{\"id\":\"A34\",\"position\":[34,1]},{\"id\":\"A35\",\"position\":[35,1]},{\"id\":\"A36\",\"position\":[36,1]},{\"id\":\"A37\",\"position\":[37,1]},{\"id\":\"A38\",\"position\":[38,1]},{\"id\":\"A39\",\"position\":[39,1]},{\"id\":\"A40\",\"position\":[40,1]},{\"id\":\"A41\",\"position\":[41,1]},{\"id\":\"A42\",\"position\":[42,1]},{\"id\":\"A43\",\"position\":[43,1]},{\"id\":\"A44\",\"position\":[44,1]},{\"id\":\"A45\",\"position\":[45,1]},{\"id\":\"A46\",\"position\":[46,1]},{\"id\":\"A47\",\"position\":[47,1]},{\"id\":\"A48\",\"position\":[48,1]},{\"id\":\"A49\",\"position\":[49,1]},{\"id\":\"A50\",\"position\":[50,1]},{\"id\":\"A51\",\"position\":[51,1]},{\"id\":\"A52\",\"position\":[52,1]},{\"id\":\"A53\",\"position\":[53,1]},{\"id\":\"A54\",\"position\":[54,1]},{\"id\":\"A55\",\"position\":[55,1]},{\"id\":\"A56\",\"position\":[56,1]},{\"id\":\"A57\",\"position\":[57,1]},{\"id\":\"A58\",\"position\":[58,1]},{\"id\":\"A59\",\"position\":[59,1]},{\"id\":\"A60\",\"position\":[60,1]},{\"id\":\"A61\",\"position\":[61,1]},{\"id\":\"A62\",\"position\":[62,1]},{\"id\":\"A63\",\"position\":[63,1]},{\"id\":\"A64\",\"position\":[64,1]},{\"id\":\"A65\",\"position\":[65,1]},{\"id\":\"A66\",\"position\":[66,1]},{\"id\":\"A67\",\"position\":[67,1]},{\"id\":\"A68\",\"position\":[68,1]},{\"id\":\"A69\",\"position\":[69,1]},{\"id\":\"A70\",\"position\":[70,1]},{\"id\":\"A71\",\"position\":[71,1]},{\"id\":\"A72\",\"position\":[72,1]},{\"id\":\"A73\",\"position\":[73,1]},{\"id\":\"A74\",\"position\":[74,1]},{\"id\":\"A75\",\"position\":[75,1]},{\"id\":\"A76\",\"position\":[76,1]},{\"id\":\"A77\",\"position\":[77,1]},{\"id\":\"A78\",\"position\":[78,1]},{\"id\":\"A79\",\"position\":[79,1]},{\"id\":\"A80\",\"position\":[80,1]},{\"id\":\"A81\",\"position\":[81,1]},{\"id\":\"A82\",\"position\":[82,1]},{\"id\":\"A83\",\"position\":[83,1]},{\"id\":\"A84\",\"position\":[84,1]},{\"id\":\"A85\",\"position\":[85,1]},{\"id\":\"A86\",\"position\":[86,1]},{\"id\":\"A87\",\"position\":[87,1]},{\"id\":\"A88\",\"position\":[88,1]},{\"id\":\"A89\",\"position\":[89,1]},{\"id\":\"A90\",\"position\":[90,1]},{\"id\":\"A91\",\"position\":[91,1]},{\"id\":\"A92\",\"position\":[92,1]},{\"id\":\"A93\",\"position\":[93,1]},{\"id\":\"A94\",\"position\":[94,1]},{\"id\":\"A95\",\"position\":[95,1]},{\"id\":\"A96\",\"position\":[96,1]},{\"id\":\"A97\",\"position\":[97,1]},{\"id\":\"A98\",\"position\":[98,1]},{\"id\":\"A99\",\"position\":[99,1]},{\"id\":\"A100\",\"position\":[100,1]}]}'),(29,'1x13','{\"dimension\": [13,1],\"row_label\": [\"A\"],\"column_label\": [1,2,3,4,5,6,7,8,9,10,11,12,13],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"A5\",\"position\":[5,1]},{\"id\":\"A6\",\"position\":[6,1]},{\"id\":\"A7\",\"position\":[7,1]},{\"id\":\"A8\",\"position\":[8,1]},{\"id\":\"A9\",\"position\":[9,1]},{\"id\":\"A10\",\"position\":[10,1]},{\"id\":\"A11\",\"position\":[11,1]},{\"id\":\"A12\",\"position\":[12,1]},{\"id\":\"A13\",\"position\":[13,1]}]}'),(30,'5x20','{\"dimension\": [20,5],\"row_label\": [\"A\",\"B\",\"C\",\"D\",\"E\"],\"column_label\": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"A5\",\"position\":[5,1]},{\"id\":\"A6\",\"position\":[6,1]},{\"id\":\"A7\",\"position\":[7,1]},{\"id\":\"A8\",\"position\":[8,1]},{\"id\":\"A9\",\"position\":[9,1]},{\"id\":\"A10\",\"position\":[10,1]},{\"id\":\"A11\",\"position\":[11,1]},{\"id\":\"A12\",\"position\":[12,1]},{\"id\":\"A13\",\"position\":[13,1]},{\"id\":\"A14\",\"position\":[14,1]},{\"id\":\"A15\",\"position\":[15,1]},{\"id\":\"A16\",\"position\":[16,1]},{\"id\":\"A17\",\"position\":[17,1]},{\"id\":\"A18\",\"position\":[18,1]},{\"id\":\"A19\",\"position\":[19,1]},{\"id\":\"A20\",\"position\":[20,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]},{\"id\":\"B4\",\"position\":[4,2]},{\"id\":\"B5\",\"position\":[5,2]},{\"id\":\"B6\",\"position\":[6,2]},{\"id\":\"B7\",\"position\":[7,2]},{\"id\":\"B8\",\"position\":[8,2]},{\"id\":\"B9\",\"position\":[9,2]},{\"id\":\"B10\",\"position\":[10,2]},{\"id\":\"B11\",\"position\":[11,2]},{\"id\":\"B12\",\"position\":[12,2]},{\"id\":\"B13\",\"position\":[13,2]},{\"id\":\"B14\",\"position\":[14,2]},{\"id\":\"B15\",\"position\":[15,2]},{\"id\":\"B16\",\"position\":[16,2]},{\"id\":\"B17\",\"position\":[17,2]},{\"id\":\"B18\",\"position\":[18,2]},{\"id\":\"B19\",\"position\":[19,2]},{\"id\":\"B20\",\"position\":[20,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"C2\",\"position\":[2,3]},{\"id\":\"C3\",\"position\":[3,3]},{\"id\":\"C4\",\"position\":[4,3]},{\"id\":\"C5\",\"position\":[5,3]},{\"id\":\"C6\",\"position\":[6,3]},{\"id\":\"C7\",\"position\":[7,3]},{\"id\":\"C8\",\"position\":[8,3]},{\"id\":\"C9\",\"position\":[9,3]},{\"id\":\"C10\",\"position\":[10,3]},{\"id\":\"C11\",\"position\":[11,3]},{\"id\":\"C12\",\"position\":[12,3]},{\"id\":\"C13\",\"position\":[13,3]},{\"id\":\"C14\",\"position\":[14,3]},{\"id\":\"C15\",\"position\":[15,3]},{\"id\":\"C16\",\"position\":[16,3]},{\"id\":\"C17\",\"position\":[17,3]},{\"id\":\"C18\",\"position\":[18,3]},{\"id\":\"C19\",\"position\":[19,3]},{\"id\":\"C20\",\"position\":[20,3]},{\"id\":\"D1\",\"position\":[1,4]},{\"id\":\"D2\",\"position\":[2,4]},{\"id\":\"D3\",\"position\":[3,4]},{\"id\":\"D4\",\"position\":[4,4]},{\"id\":\"D5\",\"position\":[5,4]},{\"id\":\"D6\",\"position\":[6,4]},{\"id\":\"D7\",\"position\":[7,4]},{\"id\":\"D8\",\"position\":[8,4]},{\"id\":\"D9\",\"position\":[9,4]},{\"id\":\"D10\",\"position\":[10,4]},{\"id\":\"D11\",\"position\":[11,4]},{\"id\":\"D12\",\"position\":[12,4]},{\"id\":\"D13\",\"position\":[13,4]},{\"id\":\"D14\",\"position\":[14,4]},{\"id\":\"D15\",\"position\":[15,4]},{\"id\":\"D16\",\"position\":[16,4]},{\"id\":\"D17\",\"position\":[17,4]},{\"id\":\"D18\",\"position\":[18,4]},{\"id\":\"D19\",\"position\":[19,4]},{\"id\":\"D20\",\"position\":[20,4]},{\"id\":\"E1\",\"position\":[1,5]},{\"id\":\"E2\",\"position\":[2,5]},{\"id\":\"E3\",\"position\":[3,5]},{\"id\":\"E4\",\"position\":[4,5]},{\"id\":\"E5\",\"position\":[5,5]},{\"id\":\"E6\",\"position\":[6,5]},{\"id\":\"E7\",\"position\":[7,5]},{\"id\":\"E8\",\"position\":[8,5]},{\"id\":\"E9\",\"position\":[9,5]},{\"id\":\"E10\",\"position\":[10,5]},{\"id\":\"E11\",\"position\":[11,5]},{\"id\":\"E12\",\"position\":[12,5]},{\"id\":\"E13\",\"position\":[13,5]},{\"id\":\"E14\",\"position\":[14,5]},{\"id\":\"E15\",\"position\":[15,5]},{\"id\":\"E16\",\"position\":[16,5]},{\"id\":\"E17\",\"position\":[17,5]},{\"id\":\"E18\",\"position\":[18,5]},{\"id\":\"E19\",\"position\":[19,5]},{\"id\":\"E20\",\"position\":[20,5]}]}'),(31,'3x13','{\"dimension\": [13,3],\"row_label\": [\"A\",\"B\",\"C\"],\"column_label\": [1,2,3,4,5,6,7,8,9,10,11,12,13],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"A5\",\"position\":[5,1]},{\"id\":\"A6\",\"position\":[6,1]},{\"id\":\"A7\",\"position\":[7,1]},{\"id\":\"A8\",\"position\":[8,1]},{\"id\":\"A9\",\"position\":[9,1]},{\"id\":\"A10\",\"position\":[10,1]},{\"id\":\"A11\",\"position\":[11,1]},{\"id\":\"A12\",\"position\":[12,1]},{\"id\":\"A13\",\"position\":[13,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]},{\"id\":\"B4\",\"position\":[4,2]},{\"id\":\"B5\",\"position\":[5,2]},{\"id\":\"B6\",\"position\":[6,2]},{\"id\":\"B7\",\"position\":[7,2]},{\"id\":\"B8\",\"position\":[8,2]},{\"id\":\"B9\",\"position\":[9,2]},{\"id\":\"B10\",\"position\":[10,2]},{\"id\":\"B11\",\"position\":[11,2]},{\"id\":\"B12\",\"position\":[12,2]},{\"id\":\"B13\",\"position\":[13,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"C2\",\"position\":[2,3]},{\"id\":\"C3\",\"position\":[3,3]},{\"id\":\"C4\",\"position\":[4,3]},{\"id\":\"C5\",\"position\":[5,3]},{\"id\":\"C6\",\"position\":[6,3]},{\"id\":\"C7\",\"position\":[7,3]},{\"id\":\"C8\",\"position\":[8,3]},{\"id\":\"C9\",\"position\":[9,3]},{\"id\":\"C10\",\"position\":[10,3]},{\"id\":\"C11\",\"position\":[11,3]},{\"id\":\"C12\",\"position\":[12,3]},{\"id\":\"C13\",\"position\":[13,3]}]}'),(32,'4x13','{\"dimension\": [13,4],\"row_label\": [\"A\",\"B\",\"C\",\"D\"],\"column_label\": [1,2,3,4,5,6,7,8,9,10,11,12,13],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"A5\",\"position\":[5,1]},{\"id\":\"A6\",\"position\":[6,1]},{\"id\":\"A7\",\"position\":[7,1]},{\"id\":\"A8\",\"position\":[8,1]},{\"id\":\"A9\",\"position\":[9,1]},{\"id\":\"A10\",\"position\":[10,1]},{\"id\":\"A11\",\"position\":[11,1]},{\"id\":\"A12\",\"position\":[12,1]},{\"id\":\"A13\",\"position\":[13,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]},{\"id\":\"B4\",\"position\":[4,2]},{\"id\":\"B5\",\"position\":[5,2]},{\"id\":\"B6\",\"position\":[6,2]},{\"id\":\"B7\",\"position\":[7,2]},{\"id\":\"B8\",\"position\":[8,2]},{\"id\":\"B9\",\"position\":[9,2]},{\"id\":\"B10\",\"position\":[10,2]},{\"id\":\"B11\",\"position\":[11,2]},{\"id\":\"B12\",\"position\":[12,2]},{\"id\":\"B13\",\"position\":[13,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"C2\",\"position\":[2,3]},{\"id\":\"C3\",\"position\":[3,3]},{\"id\":\"C4\",\"position\":[4,3]},{\"id\":\"C5\",\"position\":[5,3]},{\"id\":\"C6\",\"position\":[6,3]},{\"id\":\"C7\",\"position\":[7,3]},{\"id\":\"C8\",\"position\":[8,3]},{\"id\":\"C9\",\"position\":[9,3]},{\"id\":\"C10\",\"position\":[10,3]},{\"id\":\"C11\",\"position\":[11,3]},{\"id\":\"C12\",\"position\":[12,3]},{\"id\":\"C13\",\"position\":[13,3]},{\"id\":\"D1\",\"position\":[1,4]},{\"id\":\"D2\",\"position\":[2,4]},{\"id\":\"D3\",\"position\":[3,4]},{\"id\":\"D4\",\"position\":[4,4]},{\"id\":\"D5\",\"position\":[5,4]},{\"id\":\"D6\",\"position\":[6,4]},{\"id\":\"D7\",\"position\":[7,4]},{\"id\":\"D8\",\"position\":[8,4]},{\"id\":\"D9\",\"position\":[9,4]},{\"id\":\"D10\",\"position\":[10,4]},{\"id\":\"D11\",\"position\":[11,4]},{\"id\":\"D12\",\"position\":[12,4]},{\"id\":\"D13\",\"position\":[13,4]}]}'),(33,'1x20','{\"dimension\": [20,1],\"row_label\": [\"A\"],\"column_label\": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"A5\",\"position\":[5,1]},{\"id\":\"A6\",\"position\":[6,1]},{\"id\":\"A7\",\"position\":[7,1]},{\"id\":\"A8\",\"position\":[8,1]},{\"id\":\"A9\",\"position\":[9,1]},{\"id\":\"A10\",\"position\":[10,1]},{\"id\":\"A11\",\"position\":[11,1]},{\"id\":\"A12\",\"position\":[12,1]},{\"id\":\"A13\",\"position\":[13,1]},{\"id\":\"A14\",\"position\":[14,1]},{\"id\":\"A15\",\"position\":[15,1]},{\"id\":\"A16\",\"position\":[16,1]},{\"id\":\"A17\",\"position\":[17,1]},{\"id\":\"A18\",\"position\":[18,1]},{\"id\":\"A19\",\"position\":[19,1]},{\"id\":\"A20\",\"position\":[20,1]}]}'),(34,'4x5','{\"dimension\": [5,4],\"row_label\": [\"A\",\"B\",\"C\",\"D\"],\"column_label\": [1,2,3,4,5],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]},{\"id\":\"A3\",\"position\":[3,1]},{\"id\":\"A4\",\"position\":[4,1]},{\"id\":\"A5\",\"position\":[5,1]},{\"id\":\"B1\",\"position\":[1,2]},{\"id\":\"B2\",\"position\":[2,2]},{\"id\":\"B3\",\"position\":[3,2]},{\"id\":\"B4\",\"position\":[4,2]},{\"id\":\"B5\",\"position\":[5,2]},{\"id\":\"C1\",\"position\":[1,3]},{\"id\":\"C2\",\"position\":[2,3]},{\"id\":\"C3\",\"position\":[3,3]},{\"id\":\"C4\",\"position\":[4,3]},{\"id\":\"C5\",\"position\":[5,3]},{\"id\":\"D1\",\"position\":[1,4]},{\"id\":\"D2\",\"position\":[2,4]},{\"id\":\"D3\",\"position\":[3,4]},{\"id\":\"D4\",\"position\":[4,4]},{\"id\":\"D5\",\"position\":[5,4]}]}'),(35,'1x2','{\"dimension\": [2,1],\"row_label\": [\"A\"],\"column_label\": [1,2],\"items\": [{\"id\":\"A1\",\"position\":[1,1]},{\"id\":\"A2\",\"position\":[2,1]}]}');
/*!40000 ALTER TABLE `geometry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `input`
--

DROP TABLE IF EXISTS `input`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `input` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `operator` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `input`
--

LOCK TABLES `input` WRITE;
/*!40000 ALTER TABLE `input` DISABLE KEYS */;
/*!40000 ALTER TABLE `input` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `las_auth_session`
--

DROP TABLE IF EXISTS `las_auth_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `las_auth_session` (
  `session_key` varchar(40) NOT NULL,
  `django_session_key` varchar(40) DEFAULT NULL,
  `login_expire_date` datetime NOT NULL,
  `next_url` longtext NOT NULL,
  `session_open` tinyint(1) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_key_refs_session_key_57a5cc49` (`django_session_key`),
  CONSTRAINT `django_session_key_refs_session_key_57a5cc49` FOREIGN KEY (`django_session_key`) REFERENCES `django_session` (`session_key`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `las_auth_session`
--

LOCK TABLES `las_auth_session` WRITE;
/*!40000 ALTER TABLE `las_auth_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `las_auth_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `output`
--

DROP TABLE IF EXISTS `output`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `output` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idRequest` int(11) NOT NULL,
  `date` date NOT NULL,
  `operator` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_Output_Request1` (`idRequest`),
  CONSTRAINT `fk_Output_Request1` FOREIGN KEY (`idRequest`) REFERENCES `request` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `output`
--

LOCK TABLES `output` WRITE;
/*!40000 ALTER TABLE `output` DISABLE KEYS */;
/*!40000 ALTER TABLE `output` ENABLE KEYS */;
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
  KEY `piston_consumer_403f60f` (`user_id`),
  CONSTRAINT `user_id_refs_id_552cfef9` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
  KEY `piston_token_403f60f` (`user_id`),
  KEY `piston_token_6565fc20` (`consumer_id`),
  CONSTRAINT `consumer_id_refs_id_7a0bdcab` FOREIGN KEY (`consumer_id`) REFERENCES `piston_consumer` (`id`),
  CONSTRAINT `user_id_refs_id_103fd2e9` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `piston_token`
--

LOCK TABLES `piston_token` WRITE;
/*!40000 ALTER TABLE `piston_token` DISABLE KEYS */;
/*!40000 ALTER TABLE `piston_token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `request`
--

DROP TABLE IF EXISTS `request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `request` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `operator` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `request`
--

LOCK TABLES `request` WRITE;
/*!40000 ALTER TABLE `request` DISABLE KEYS */;
/*!40000 ALTER TABLE `request` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `storage_wg`
--

DROP TABLE IF EXISTS `storage_wg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `storage_wg` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `storage_wg_5d52dd10` (`owner_id`),
  CONSTRAINT `owner_id_refs_id_d6eed27b` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `storage_wg`
--

LOCK TABLES `storage_wg` WRITE;
/*!40000 ALTER TABLE `storage_wg` DISABLE KEYS */;
/*!40000 ALTER TABLE `storage_wg` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `storage_wg_user`
--

DROP TABLE IF EXISTS `storage_wg_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `storage_wg_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `WG_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `storage_wg_user_e2a12238` (`WG_id`),
  KEY `storage_wg_user_fbfc09f1` (`user_id`),
  KEY `storage_wg_user_1e014c8f` (`permission_id`),
  CONSTRAINT `permission_id_refs_id_2fe3d2b0` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `user_id_refs_id_ad0772ce` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `WG_id_refs_id_1fcabd38` FOREIGN KEY (`WG_id`) REFERENCES `storage_wg` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1696 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `storage_wg_user`
--

LOCK TABLES `storage_wg_user` WRITE;
/*!40000 ALTER TABLE `storage_wg_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `storage_wg_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `url`
--

DROP TABLE IF EXISTS `url`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `url` (
  `id` int(11) NOT NULL,
  `url` varchar(60) NOT NULL,
  `default` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `url`
--

LOCK TABLES `url` WRITE;
/*!40000 ALTER TABLE `url` DISABLE KEYS */;
INSERT INTO `url` VALUES (1,'http://emageda.polito.it:7000',0),(2,'http://devircc.polito.it/biobank',0),(3,'/biobank',1);
/*!40000 ALTER TABLE `url` ENABLE KEYS */;
UNLOCK TABLES;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-11-11  2:00:13
