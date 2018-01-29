-- MySQL dump 10.13  Distrib 5.5.35, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: cellline
-- ------------------------------------------------------
-- Server version	5.5.35-0ubuntu0.12.04.2

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
-- Table structure for table `aliquots`
--

DROP TABLE IF EXISTS `aliquots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquots` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gen_id` varchar(26) NOT NULL,
  `archive_details_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `aliquotID_UNIQUE` (`gen_id`),
  KEY `fk_aliquots_archive_details1` (`archive_details_id`),
  CONSTRAINT `fk_aliquots_archive_details1` FOREIGN KEY (`archive_details_id`) REFERENCES `archive_details` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquots`
--

LOCK TABLES `aliquots` WRITE;
/*!40000 ALTER TABLE `aliquots` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliquots` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `allowed_values`
--

DROP TABLE IF EXISTS `allowed_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `allowed_values` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `allowed_value` varchar(45) NOT NULL,
  `condition_feature_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ind` (`allowed_value`,`condition_feature_id`),
  KEY `fk_allowed_values_condition_feature1` (`condition_feature_id`),
  CONSTRAINT `fk_allowed_values_condition_feature1` FOREIGN KEY (`condition_feature_id`) REFERENCES `condition_feature` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `allowed_values`
--

LOCK TABLES `allowed_values` WRITE;
/*!40000 ALTER TABLE `allowed_values` DISABLE KEYS */;
INSERT INTO `allowed_values` VALUES (3,'adherent (A)',14),(2,'expansion',13),(1,'generation',13),(4,'suspended (S)',14);
/*!40000 ALTER TABLE `allowed_values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `archive_details`
--

DROP TABLE IF EXISTS `archive_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `archive_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `experiment_in_vitro_id` int(11) DEFAULT NULL,
  `events_id` int(11) DEFAULT NULL,
  `amount` int(11) NOT NULL,
  `application_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_storage_event_experiment_in_vitro1_idx` (`experiment_in_vitro_id`),
  KEY `fk_archive_details_events1_idx` (`events_id`),
  CONSTRAINT `fk_storage_event_experiment_in_vitro1` FOREIGN KEY (`experiment_in_vitro_id`) REFERENCES `experiment_in_vitro` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_archive_details_events1` FOREIGN KEY (`events_id`) REFERENCES `events` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `archive_details`
--

LOCK TABLES `archive_details` WRITE;
/*!40000 ALTER TABLE `archive_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `archive_details` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can add group',2,'add_group'),(5,'Can change group',2,'change_group'),(6,'Can delete group',2,'delete_group'),(7,'Can add user',3,'add_user'),(8,'Can change user',3,'change_user'),(9,'Can delete user',3,'delete_user'),(10,'Can add content type',4,'add_contenttype'),(11,'Can change content type',4,'change_contenttype'),(12,'Can delete content type',4,'delete_contenttype'),(13,'Can add session',5,'add_session'),(14,'Can change session',5,'change_session'),(15,'Can delete session',5,'delete_session'),(16,'Can add site',6,'add_site'),(17,'Can change site',6,'change_site'),(18,'Can delete site',6,'delete_site'),(19,'Can add log entry',7,'add_logentry'),(20,'Can change log entry',7,'change_logentry'),(21,'Can delete log entry',7,'delete_logentry'),(22,'Can add url handler',8,'add_urlhandler'),(23,'Can change url handler',8,'change_urlhandler'),(24,'Can delete url handler',8,'delete_urlhandler'),(25,'Can add cancer research group',9,'add_cancerresearchgroup'),(26,'Can change cancer research group',9,'change_cancerresearchgroup'),(27,'Can delete cancer research group',9,'delete_cancerresearchgroup'),(28,'Can add institution',10,'add_institution'),(29,'Can change institution',10,'change_institution'),(30,'Can delete institution',10,'delete_institution'),(31,'Can add cell line users',11,'add_celllineusers'),(32,'Can change cell line users',11,'change_celllineusers'),(33,'Can delete cell line users',11,'delete_celllineusers'),(34,'Can add condition protocol type',12,'add_conditionprotocoltype'),(35,'Can change condition protocol type',12,'change_conditionprotocoltype'),(36,'Can delete condition protocol type',12,'delete_conditionprotocoltype'),(37,'Can add condition protocol element',13,'add_conditionprotocolelement'),(38,'Can change condition protocol element',13,'change_conditionprotocolelement'),(39,'Can delete condition protocol element',13,'delete_conditionprotocolelement'),(40,'Can add condition configuration',14,'add_conditionconfiguration'),(41,'Can change condition configuration',14,'change_conditionconfiguration'),(42,'Can delete condition configuration',14,'delete_conditionconfiguration'),(43,'Can add condition feature',15,'add_conditionfeature'),(44,'Can change condition feature',15,'change_conditionfeature'),(45,'Can delete condition feature',15,'delete_conditionfeature'),(46,'Can add condition protocol_has_ feature',16,'add_conditionprotocol_has_feature'),(47,'Can change condition protocol_has_ feature',16,'change_conditionprotocol_has_feature'),(48,'Can delete condition protocol_has_ feature',16,'delete_conditionprotocol_has_feature'),(49,'Can add condition_has_ feature',17,'add_condition_has_feature'),(50,'Can change condition_has_ feature',17,'change_condition_has_feature'),(51,'Can delete condition_has_ feature',17,'delete_condition_has_feature'),(52,'Can add request',18,'add_request'),(53,'Can change request',18,'change_request'),(54,'Can delete request',18,'delete_request'),(55,'Can add aliquots',19,'add_aliquots'),(56,'Can change aliquots',19,'change_aliquots'),(57,'Can delete aliquots',19,'delete_aliquots'),(58,'Can add aliquots_has_ request',20,'add_aliquots_has_request'),(59,'Can change aliquots_has_ request',20,'change_aliquots_has_request'),(60,'Can delete aliquots_has_ request',20,'delete_aliquots_has_request'),(61,'Can add expansion event',21,'add_expansionevent'),(62,'Can change expansion event',21,'change_expansionevent'),(63,'Can delete expansion event',21,'delete_expansionevent'),(64,'Can add cells',22,'add_cells'),(65,'Can change cells',22,'change_cells'),(66,'Can delete cells',22,'delete_cells'),(67,'Can add time',23,'add_time'),(68,'Can change time',23,'change_time'),(69,'Can delete time',23,'delete_time'),(70,'Can add cell details',24,'add_celldetails'),(71,'Can change cell details',24,'change_celldetails'),(72,'Can delete cell details',24,'delete_celldetails'),(73,'Can add experiment event',25,'add_experimentevent'),(74,'Can change experiment event',25,'change_experimentevent'),(75,'Can delete experiment event',25,'delete_experimentevent'),(76,'Can add experiment in vitro',26,'add_experimentinvitro'),(77,'Can change experiment in vitro',26,'change_experimentinvitro'),(78,'Can delete experiment in vitro',26,'delete_experimentinvitro'),(79,'Can add gen i d_archive',27,'add_genid_archive'),(80,'Can change gen i d_archive',27,'change_genid_archive'),(81,'Can delete gen i d_archive',27,'delete_genid_archive'),(82,'Can add gen i d_generation',28,'add_genid_generation'),(83,'Can change gen i d_generation',28,'change_genid_generation'),(84,'Can delete gen i d_generation',28,'delete_genid_generation'),(85,'Can add gen i d_parte1_generation',29,'add_genid_parte1_generation'),(86,'Can change gen i d_parte1_generation',29,'change_genid_parte1_generation'),(87,'Can delete gen i d_parte1_generation',29,'delete_genid_parte1_generation'),(88,'Can add gen i d_parte2_generation',30,'add_genid_parte2_generation'),(89,'Can change gen i d_parte2_generation',30,'change_genid_parte2_generation'),(90,'Can delete gen i d_parte2_generation',30,'delete_genid_parte2_generation'),(91,'Can add gen i d_letters_generation',31,'add_genid_letters_generation'),(92,'Can change gen i d_letters_generation',31,'change_genid_letters_generation'),(93,'Can delete gen i d_letters_generation',31,'delete_genid_letters_generation'),(94,'Can add cult cond list_ name type',32,'add_cultcondlist_nametype'),(95,'Can change cult cond list_ name type',32,'change_cultcondlist_nametype'),(96,'Can delete cult cond list_ name type',32,'delete_cultcondlist_nametype'),(97,'Can add plate number',33,'add_platenumber'),(98,'Can change plate number',33,'change_platenumber'),(99,'Can delete plate number',33,'delete_platenumber'),(100,'Can add plate name',34,'add_platename'),(101,'Can change plate name',34,'change_platename'),(102,'Can delete plate name',34,'delete_platename'),(103,'Can add archive table',35,'add_archivetable'),(104,'Can change archive table',35,'change_archivetable'),(105,'Can delete archive table',35,'delete_archivetable'),(106,'Can add las_auth_session',36,'add_lasauthsession'),(107,'Can change las_auth_session',36,'change_lasauthsession'),(108,'Can delete las_auth_session',36,'delete_lasauthsession'),(109,'Can add nonce',37,'add_nonce'),(110,'Can change nonce',37,'change_nonce'),(111,'Can delete nonce',37,'delete_nonce'),(112,'Can add resource',38,'add_resource'),(113,'Can change resource',38,'change_resource'),(114,'Can delete resource',38,'delete_resource'),(115,'Can add consumer',39,'add_consumer'),(116,'Can change consumer',39,'change_consumer'),(117,'Can delete consumer',39,'delete_consumer'),(118,'Can add token',40,'add_token'),(119,'Can change token',40,'change_token'),(120,'Can delete token',40,'delete_token');
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'piero','','','p@t.it','pbkdf2_sha256$10000$izHJavHrBNtY$V/kJ72orBjmNt8kcikecPZNsWdrAfV5IOP9K7KOwP8U=',1,1,1,'2014-02-26 10:42:30','2013-03-14 16:19:07');
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cancer_research_group`
--

DROP TABLE IF EXISTS `cancer_research_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cancer_research_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cancer_research_group`
--

LOCK TABLES `cancer_research_group` WRITE;
/*!40000 ALTER TABLE `cancer_research_group` DISABLE KEYS */;
INSERT INTO `cancer_research_group` VALUES (1,'Bardelli');
/*!40000 ALTER TABLE `cancer_research_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cell_details`
--

DROP TABLE IF EXISTS `cell_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cell_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `num_plates` int(11) NOT NULL,
  `start_date_time` datetime NOT NULL,
  `cells_id` int(11) NOT NULL,
  `condition_configuration_id` int(11) NOT NULL,
  `end_date_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `CellLineApp_celldetails_713b1aa` (`cells_id`),
  KEY `CellLineApp_celldetails_66a6d117` (`condition_configuration_id`),
  CONSTRAINT `cells_id_refs_id_6c542984` FOREIGN KEY (`cells_id`) REFERENCES `cells` (`id`),
  CONSTRAINT `conditionConfiguration_id_refs_id_20ab20fb` FOREIGN KEY (`condition_configuration_id`) REFERENCES `condition_configuration` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cell_details`
--

LOCK TABLES `cell_details` WRITE;
/*!40000 ALTER TABLE `cell_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `cell_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cellline_users`
--

DROP TABLE IF EXISTS `cellline_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cellline_users` (
  `user_ptr_id` int(11) NOT NULL,
  `institution_id` int(11) DEFAULT NULL,
  `cancer_research_group_id` int(11) DEFAULT NULL,
  `supervisor_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`user_ptr_id`),
  KEY `CellLineApp_celllineusers_5e29f20d` (`institution_id`),
  KEY `CellLineApp_celllineusers_326a24f7` (`cancer_research_group_id`),
  KEY `CellLineApp_celllineusers_561f4514` (`supervisor_id`),
  CONSTRAINT `id_supervisor_refs_id_49f13a7` FOREIGN KEY (`supervisor_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `cancerResearchGroup_id_refs_id_7a36ee67` FOREIGN KEY (`cancer_research_group_id`) REFERENCES `cancer_research_group` (`id`),
  CONSTRAINT `institution_id_refs_id_23d6c4b7` FOREIGN KEY (`institution_id`) REFERENCES `institution` (`id`),
  CONSTRAINT `user_ptr_id_refs_id_49f13a7` FOREIGN KEY (`user_ptr_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cellline_users`
--

LOCK TABLES `cellline_users` WRITE;
/*!40000 ALTER TABLE `cellline_users` DISABLE KEYS */;
INSERT INTO `cellline_users` VALUES (1,1,1,1);
/*!40000 ALTER TABLE `cellline_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cells`
--

DROP TABLE IF EXISTS `cells`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cells` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `genID` varchar(26) NOT NULL,
  `nickname` varchar(45) DEFAULT NULL,
  `nickid` varchar(5) DEFAULT NULL,
  `cancer_research_group_id` int(11) NOT NULL,
  `expansion_details_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `CellLineApp_cells_326a24f7` (`cancer_research_group_id`),
  KEY `CellLineApp_cells_156023c3` (`expansion_details_id`),
  CONSTRAINT `cancerResearchGroup_id_refs_id_56393b6c` FOREIGN KEY (`cancer_research_group_id`) REFERENCES `cancer_research_group` (`id`),
  CONSTRAINT `expansionEvent_id_refs_id_51aa54a8` FOREIGN KEY (`expansion_details_id`) REFERENCES `expansion_details` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cells`
--

LOCK TABLES `cells` WRITE;
/*!40000 ALTER TABLE `cells` DISABLE KEYS */;
/*!40000 ALTER TABLE `cells` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cells_has_aliquots`
--

DROP TABLE IF EXISTS `cells_has_aliquots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cells_has_aliquots` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `aliquots_id` int(11) NOT NULL,
  `cells_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_table1_aliquots1_idx` (`aliquots_id`),
  KEY `fk_table1_cells1_idx` (`cells_id`),
  CONSTRAINT `fk_table1_aliquots1` FOREIGN KEY (`aliquots_id`) REFERENCES `aliquots` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_table1_cells1` FOREIGN KEY (`cells_id`) REFERENCES `cells` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cells_has_aliquots`
--

LOCK TABLES `cells_has_aliquots` WRITE;
/*!40000 ALTER TABLE `cells_has_aliquots` DISABLE KEYS */;
/*!40000 ALTER TABLE `cells_has_aliquots` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `condition_configuration`
--

DROP TABLE IF EXISTS `condition_configuration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `condition_configuration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `version` int(11) NOT NULL,
  `condition_protocol_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_condition_configuration_condition_protocol1` (`condition_protocol_id`),
  CONSTRAINT `fk_condition_configuration_condition_protocol1` FOREIGN KEY (`condition_protocol_id`) REFERENCES `condition_protocol` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `condition_configuration`
--

LOCK TABLES `condition_configuration` WRITE;
/*!40000 ALTER TABLE `condition_configuration` DISABLE KEYS */;
INSERT INTO `condition_configuration` VALUES (1,0,1),(2,0,2),(3,0,3),(4,0,4),(5,0,5),(6,0,6),(7,0,7),(8,0,8),(9,0,9),(10,0,10),(11,0,11),(12,0,12),(13,0,13),(14,0,14),(15,0,15),(16,0,16),(17,0,17),(18,0,18),(19,0,19),(20,0,20),(21,0,21),(22,0,22),(23,0,23),(24,0,24),(25,0,25),(26,0,26),(27,0,27),(28,0,28),(29,0,29),(30,0,30),(31,0,31),(32,0,32),(33,0,33),(34,0,34),(35,0,35),(36,0,36),(37,0,37),(38,0,38),(39,0,39),(40,0,40),(41,0,41),(42,0,42),(43,0,43),(44,0,44),(45,0,45),(46,0,46),(47,0,47),(48,0,48),(49,0,49),(50,0,50),(51,0,51),(52,0,52),(53,0,53),(54,0,54),(55,0,55),(56,0,56),(57,0,57);
/*!40000 ALTER TABLE `condition_configuration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `condition_feature`
--

DROP TABLE IF EXISTS `condition_feature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `condition_feature` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `unity_measure` varchar(10) DEFAULT NULL,
  `default_value` varchar(45) DEFAULT NULL,
  `condition_protocol_element_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_condition_feature_condition_protocol_element1` (`condition_protocol_element_id`),
  CONSTRAINT `fk_condition_feature_condition_protocol_element1` FOREIGN KEY (`condition_protocol_element_id`) REFERENCES `condition_protocol_element` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `condition_feature`
--

LOCK TABLES `condition_feature` WRITE;
/*!40000 ALTER TABLE `condition_feature` DISABLE KEYS */;
INSERT INTO `condition_feature` VALUES (1,'percentage','%','',15),(2,'percentage','%','',16),(3,'percentage','%','',6),(4,'percentage','%','',7),(5,'dosage','mg/ml','',8),(6,'dosage','mM','',9),(7,'dosage','ug/ml','',10),(8,'dosage','ug/ml','',11),(9,'dosage','ug/ml','',12),(10,'dosage','ug/ml','',27),(11,'percentage','%','',13),(12,'percentage','%','',14),(13,'type_protocol',NULL,NULL,NULL),(14,'type_process',NULL,NULL,NULL),(15,'type_plate',NULL,NULL,NULL),(16,'No feature',NULL,NULL,17),(17,'No feature',NULL,NULL,18),(18,'No feature',NULL,NULL,19),(20,'No feature',NULL,NULL,21),(21,'No feature',NULL,NULL,22),(22,'No feature',NULL,NULL,23),(23,'No feature',NULL,NULL,24),(25,'No feature',NULL,NULL,26),(26,'percentage','%','',28),(27,'percentage','%','',29);
/*!40000 ALTER TABLE `condition_feature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `condition_has_feature`
--

DROP TABLE IF EXISTS `condition_has_feature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `condition_has_feature` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` varchar(30) DEFAULT NULL,
  `condition_feature_id` int(11) NOT NULL,
  `condition_configuration_id` int(11) NOT NULL,
  `start` int(11) DEFAULT NULL,
  `end` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `CellLineApp_condition_has_feature_474d171f` (`condition_feature_id`),
  KEY `CellLineApp_condition_has_feature_66a6d117` (`condition_configuration_id`),
  CONSTRAINT `conditionConfiguration_id_refs_id_6793b72c` FOREIGN KEY (`condition_configuration_id`) REFERENCES `condition_configuration` (`id`),
  CONSTRAINT `conditionFeature_id_refs_id_1e58dd82` FOREIGN KEY (`condition_feature_id`) REFERENCES `condition_feature` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=423 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `condition_has_feature`
--

LOCK TABLES `condition_has_feature` WRITE;
/*!40000 ALTER TABLE `condition_has_feature` DISABLE KEYS */;
INSERT INTO `condition_has_feature` VALUES (1,'PlateThermoStandard',15,1,NULL,NULL),(2,'adherent (A)',14,1,NULL,NULL),(3,'expansion',13,1,NULL,NULL),(4,'10',1,1,NULL,NULL),(5,'1',11,1,NULL,NULL),(6,'-',16,1,NULL,NULL),(7,'PlateThermoStandard',15,2,NULL,NULL),(8,'adherent (A)',14,2,NULL,NULL),(9,'expansion',13,2,NULL,NULL),(10,'-',17,2,NULL,NULL),(11,'10',1,2,NULL,NULL),(12,'1',11,2,NULL,NULL),(13,'PlateThermoStandard',15,3,NULL,NULL),(14,'adherent (A)',14,3,NULL,NULL),(15,'expansion',13,3,NULL,NULL),(16,'-',18,3,NULL,NULL),(17,'10',1,3,NULL,NULL),(18,'1',11,3,NULL,NULL),(19,'PlateThermoStandard',15,4,NULL,NULL),(20,'adherent (A)',14,4,NULL,NULL),(21,'expansion',13,4,NULL,NULL),(22,'-',20,4,NULL,NULL),(23,'20',1,4,NULL,NULL),(24,'-',21,4,NULL,NULL),(25,'1',11,4,NULL,NULL),(26,'PlateThermoStandard',15,5,NULL,NULL),(27,'adherent (A)',14,5,NULL,NULL),(28,'expansion',13,5,NULL,NULL),(29,'10',1,5,NULL,NULL),(30,'1',11,5,NULL,NULL),(31,'-',21,5,NULL,NULL),(32,'PlateThermoStandard',15,6,NULL,NULL),(33,'adherent (A)',14,6,NULL,NULL),(34,'expansion',13,6,NULL,NULL),(35,'-',20,6,NULL,NULL),(36,'10',1,6,NULL,NULL),(37,'1',11,6,NULL,NULL),(38,'PlateThermoStandard',15,7,NULL,NULL),(39,'adherent (A)',14,7,NULL,NULL),(40,'expansion',13,7,NULL,NULL),(41,'-',18,7,NULL,NULL),(42,'10',1,7,NULL,NULL),(43,'1',4,7,NULL,NULL),(44,'1',11,7,NULL,NULL),(45,'PlateThermoStandard',15,8,NULL,NULL),(46,'adherent (A)',14,8,NULL,NULL),(47,'expansion',13,8,NULL,NULL),(48,'5',1,8,NULL,NULL),(49,'1',11,8,NULL,NULL),(50,'-',21,8,NULL,NULL),(51,'PlateThermoStandard',15,9,NULL,NULL),(52,'adherent (A)',14,9,NULL,NULL),(53,'expansion',13,9,NULL,NULL),(54,'-',20,9,NULL,NULL),(55,'10',1,9,NULL,NULL),(56,'-',21,9,NULL,NULL),(57,'1',11,9,NULL,NULL),(58,'PlateThermoStandard',15,10,NULL,NULL),(59,'adherent (A)',14,10,NULL,NULL),(60,'expansion',13,10,NULL,NULL),(61,'-',17,10,NULL,NULL),(62,'10',1,10,NULL,NULL),(63,'1',5,10,NULL,NULL),(64,'1',11,10,NULL,NULL),(65,'PlateThermoStandard',15,11,NULL,NULL),(66,'adherent (A)',14,11,NULL,NULL),(67,'expansion',13,11,NULL,NULL),(68,'15',1,11,NULL,NULL),(69,'1',11,11,NULL,NULL),(70,'-',21,11,NULL,NULL),(71,'PlateThermoStandard',15,12,NULL,NULL),(72,'adherent (A)',14,12,NULL,NULL),(73,'expansion',13,12,NULL,NULL),(74,'10',1,12,NULL,NULL),(75,'1',11,12,NULL,NULL),(76,'-',22,12,NULL,NULL),(77,'0.03',10,12,NULL,NULL),(78,'PlateThermoStandard',15,13,NULL,NULL),(79,'adherent (A)',14,13,NULL,NULL),(80,'expansion',13,13,NULL,NULL),(81,'-',20,13,NULL,NULL),(82,'10',1,13,NULL,NULL),(83,'-',21,13,NULL,NULL),(84,'1',11,13,NULL,NULL),(85,'1',6,13,NULL,NULL),(86,'PlateThermoStandard',15,14,NULL,NULL),(87,'adherent (A)',14,14,NULL,NULL),(88,'expansion',13,14,NULL,NULL),(89,'-',20,14,NULL,NULL),(90,'10',1,14,NULL,NULL),(91,'-',21,14,NULL,NULL),(92,'10',5,14,NULL,NULL),(93,'1',11,14,NULL,NULL),(94,'PlateThermoStandard',15,15,NULL,NULL),(95,'adherent (A)',14,15,NULL,NULL),(96,'expansion',13,15,NULL,NULL),(97,'-',20,15,NULL,NULL),(98,'1',11,15,NULL,NULL),(99,'-',21,15,NULL,NULL),(100,'10',1,15,NULL,NULL),(101,'100000',10,15,NULL,NULL),(102,'PlateThermoStandard',15,16,NULL,NULL),(103,'adherent (A)',14,16,NULL,NULL),(104,'expansion',13,16,NULL,NULL),(105,'-',20,16,NULL,NULL),(106,'10',1,16,NULL,NULL),(107,'-',21,16,NULL,NULL),(108,'50',7,16,NULL,NULL),(109,'1',11,16,NULL,NULL),(110,'PlateThermoStandard',15,17,NULL,NULL),(111,'adherent (A)',14,17,NULL,NULL),(112,'expansion',13,17,NULL,NULL),(113,'10',1,17,NULL,NULL),(114,'1',11,17,NULL,NULL),(115,'50',7,17,NULL,NULL),(116,'10',5,17,NULL,NULL),(117,'-',20,17,NULL,NULL),(118,'-',21,17,NULL,NULL),(119,'100000',10,17,NULL,NULL),(120,'PlateThermoStandard',15,18,NULL,NULL),(121,'adherent (A)',14,18,NULL,NULL),(122,'expansion',13,18,NULL,NULL),(123,'10',1,18,NULL,NULL),(124,'1',11,18,NULL,NULL),(125,'PlateThermoStandard',15,19,NULL,NULL),(126,'adherent (A)',14,19,NULL,NULL),(127,'expansion',13,19,NULL,NULL),(128,'-',17,19,NULL,NULL),(129,'-',20,19,NULL,NULL),(130,'10',1,19,NULL,NULL),(131,'1',11,19,NULL,NULL),(132,'-',23,18,NULL,NULL),(133,'PlateThermoStandard',15,20,NULL,NULL),(134,'adherent (A)',14,20,NULL,NULL),(135,'expansion',13,20,NULL,NULL),(136,'-',20,20,NULL,NULL),(137,'5',1,20,NULL,NULL),(138,'-',21,20,NULL,NULL),(139,'1',11,20,NULL,NULL),(140,'PlateThermoStandard',15,21,NULL,NULL),(141,'adherent (A)',14,21,NULL,NULL),(142,'expansion',13,21,NULL,NULL),(143,'-',18,21,NULL,NULL),(144,'2',1,21,NULL,NULL),(145,'1',12,21,NULL,NULL),(146,'2',8,21,NULL,NULL),(147,'PlateThermoStandard',15,22,NULL,NULL),(148,'adherent (A)',14,22,NULL,NULL),(149,'expansion',13,22,NULL,NULL),(150,'-',18,22,NULL,NULL),(151,'2',1,22,NULL,NULL),(152,'0.86',9,22,NULL,NULL),(153,'PlateThermoStandard',15,23,NULL,NULL),(154,'adherent (A)',14,23,NULL,NULL),(155,'expansion',13,23,NULL,NULL),(156,'-',18,23,NULL,NULL),(157,'2',1,23,NULL,NULL),(158,'10',5,23,NULL,NULL),(159,'PlateThermoStandard',15,24,NULL,NULL),(160,'adherent (A)',14,24,NULL,NULL),(161,'expansion',13,24,NULL,NULL),(162,'-',18,24,NULL,NULL),(163,'2',1,24,NULL,NULL),(164,'1',7,24,NULL,NULL),(165,'PlateThermoStandard',15,25,NULL,NULL),(166,'adherent (A)',14,25,NULL,NULL),(167,'expansion',13,25,NULL,NULL),(168,'-',18,25,NULL,NULL),(169,'1',11,25,NULL,NULL),(170,'8',2,25,NULL,NULL),(171,'PlateThermoStandard',15,26,NULL,NULL),(172,'adherent (A)',14,26,NULL,NULL),(173,'expansion',13,26,NULL,NULL),(174,'10',1,26,NULL,NULL),(175,'-',25,26,NULL,NULL),(176,'1',11,26,NULL,NULL),(177,'PlateThermoStandard',15,27,NULL,NULL),(178,'adherent (A)',14,27,NULL,NULL),(179,'expansion',13,27,NULL,NULL),(180,'45',1,27,NULL,NULL),(181,'1',11,27,NULL,NULL),(182,'10',3,27,NULL,NULL),(183,'-',16,27,NULL,NULL),(184,'PlateThermoStandard',15,28,NULL,NULL),(185,'adherent (A)',14,28,NULL,NULL),(186,'expansion',13,28,NULL,NULL),(187,'-',17,28,NULL,NULL),(188,'45',1,28,NULL,NULL),(189,'10',3,28,NULL,NULL),(190,'1',11,28,NULL,NULL),(191,'PlateThermoStandard',15,29,NULL,NULL),(192,'adherent (A)',14,29,NULL,NULL),(193,'expansion',13,29,NULL,NULL),(194,'-',18,29,NULL,NULL),(195,'45',1,29,NULL,NULL),(196,'10',3,29,NULL,NULL),(197,'1',11,29,NULL,NULL),(198,'PlateThermoStandard',15,30,NULL,NULL),(199,'adherent (A)',14,30,NULL,NULL),(200,'expansion',13,30,NULL,NULL),(201,'-',20,30,NULL,NULL),(202,'45',1,30,NULL,NULL),(203,'-',21,30,NULL,NULL),(204,'1',11,30,NULL,NULL),(205,'10',3,30,NULL,NULL),(206,'PlateThermoStandard',15,31,NULL,NULL),(207,'adherent (A)',14,31,NULL,NULL),(208,'expansion',13,31,NULL,NULL),(209,'45',1,31,NULL,NULL),(210,'1',11,31,NULL,NULL),(211,'-',21,31,NULL,NULL),(212,'10',3,31,NULL,NULL),(213,'PlateThermoStandard',15,32,NULL,NULL),(214,'adherent (A)',14,32,NULL,NULL),(215,'expansion',13,32,NULL,NULL),(216,'-',20,32,NULL,NULL),(217,'45',1,32,NULL,NULL),(218,'10',3,32,NULL,NULL),(219,'1',11,32,NULL,NULL),(220,'PlateThermoStandard',15,33,NULL,NULL),(221,'adherent (A)',14,33,NULL,NULL),(222,'expansion',13,33,NULL,NULL),(223,'-',18,33,NULL,NULL),(224,'45',1,33,NULL,NULL),(225,'10',3,33,NULL,NULL),(226,'1',4,33,NULL,NULL),(227,'1',11,33,NULL,NULL),(228,'PlateThermoStandard',15,34,NULL,NULL),(229,'adherent (A)',14,34,NULL,NULL),(230,'expansion',13,34,NULL,NULL),(231,'45',1,34,NULL,NULL),(232,'1',11,34,NULL,NULL),(233,'-',21,34,NULL,NULL),(234,'10',3,34,NULL,NULL),(235,'PlateThermoStandard',15,35,NULL,NULL),(236,'adherent (A)',14,35,NULL,NULL),(237,'expansion',13,35,NULL,NULL),(238,'-',20,35,NULL,NULL),(239,'1',11,35,NULL,NULL),(240,'-',21,35,NULL,NULL),(241,'45',1,35,NULL,NULL),(242,'10',3,35,NULL,NULL),(243,'PlateThermoStandard',15,36,NULL,NULL),(244,'adherent (A)',14,36,NULL,NULL),(245,'expansion',13,36,NULL,NULL),(246,'-',17,36,NULL,NULL),(247,'45',1,36,NULL,NULL),(248,'10',3,36,NULL,NULL),(249,'1',5,36,NULL,NULL),(250,'1',11,36,NULL,NULL),(251,'PlateThermoStandard',15,37,NULL,NULL),(252,'adherent (A)',14,37,NULL,NULL),(253,'expansion',13,37,NULL,NULL),(254,'45',1,37,NULL,NULL),(255,'1',11,37,NULL,NULL),(256,'-',21,37,NULL,NULL),(257,'10',3,37,NULL,NULL),(258,'PlateThermoStandard',15,38,NULL,NULL),(259,'adherent (A)',14,38,NULL,NULL),(260,'expansion',13,38,NULL,NULL),(261,'45',1,38,NULL,NULL),(262,'1',11,38,NULL,NULL),(263,'10',3,38,NULL,NULL),(264,'-',22,38,NULL,NULL),(265,'0.03',10,38,NULL,NULL),(266,'PlateThermoStandard',15,39,NULL,NULL),(267,'adherent (A)',14,39,NULL,NULL),(268,'expansion',13,39,NULL,NULL),(269,'45',1,39,NULL,NULL),(270,'1',11,39,NULL,NULL),(271,'10',3,39,NULL,NULL),(272,'1',6,39,NULL,NULL),(273,'-',20,39,NULL,NULL),(274,'-',21,39,NULL,NULL),(275,'PlateThermoStandard',15,40,NULL,NULL),(276,'adherent (A)',14,40,NULL,NULL),(277,'expansion',13,40,NULL,NULL),(278,'45',1,40,NULL,NULL),(279,'1',11,40,NULL,NULL),(280,'10',3,40,NULL,NULL),(281,'10',5,40,NULL,NULL),(282,'-',20,40,NULL,NULL),(283,'-',21,40,NULL,NULL),(284,'PlateThermoStandard',15,41,NULL,NULL),(285,'adherent (A)',14,41,NULL,NULL),(286,'expansion',13,41,NULL,NULL),(287,'45',1,41,NULL,NULL),(288,'1',11,41,NULL,NULL),(289,'10',3,41,NULL,NULL),(290,'-',20,41,NULL,NULL),(291,'-',21,41,NULL,NULL),(292,'100000',10,41,NULL,NULL),(293,'PlateThermoStandard',15,42,NULL,NULL),(294,'adherent (A)',14,42,NULL,NULL),(295,'expansion',13,42,NULL,NULL),(296,'45',1,42,NULL,NULL),(297,'1',11,42,NULL,NULL),(298,'10',3,42,NULL,NULL),(299,'50',7,42,NULL,NULL),(300,'-',20,42,NULL,NULL),(301,'-',21,42,NULL,NULL),(302,'PlateThermoStandard',15,43,NULL,NULL),(303,'adherent (A)',14,43,NULL,NULL),(304,'expansion',13,43,NULL,NULL),(305,'45',1,43,NULL,NULL),(306,'1',11,43,NULL,NULL),(307,'10',3,43,NULL,NULL),(308,'50',7,43,NULL,NULL),(309,'10',5,43,NULL,NULL),(310,'-',20,43,NULL,NULL),(311,'-',21,43,NULL,NULL),(312,'100000',10,43,NULL,NULL),(313,'PlateThermoStandard',15,44,NULL,NULL),(314,'adherent (A)',14,44,NULL,NULL),(315,'expansion',13,44,NULL,NULL),(316,'45',1,44,NULL,NULL),(317,'1',11,44,NULL,NULL),(318,'-',23,44,NULL,NULL),(319,'10',3,44,NULL,NULL),(320,'PlateThermoStandard',15,45,NULL,NULL),(321,'adherent (A)',14,45,NULL,NULL),(322,'expansion',13,45,NULL,NULL),(323,'-',17,45,NULL,NULL),(324,'-',20,45,NULL,NULL),(325,'10',3,45,NULL,NULL),(326,'45',1,45,NULL,NULL),(327,'1',11,45,NULL,NULL),(328,'PlateThermoStandard',15,46,NULL,NULL),(329,'adherent (A)',14,46,NULL,NULL),(330,'expansion',13,46,NULL,NULL),(331,'-',20,46,NULL,NULL),(332,'1',11,46,NULL,NULL),(333,'-',21,46,NULL,NULL),(334,'45',1,46,NULL,NULL),(335,'10',3,46,NULL,NULL),(336,'PlateThermoStandard',15,47,NULL,NULL),(337,'adherent (A)',14,47,NULL,NULL),(338,'expansion',13,47,NULL,NULL),(339,'-',18,47,NULL,NULL),(340,'45',1,47,NULL,NULL),(341,'10',3,47,NULL,NULL),(342,'1',12,47,NULL,NULL),(343,'2',8,47,NULL,NULL),(344,'PlateThermoStandard',15,48,NULL,NULL),(345,'adherent (A)',14,48,NULL,NULL),(346,'expansion',13,48,NULL,NULL),(347,'-',18,48,NULL,NULL),(348,'45',1,48,NULL,NULL),(349,'10',3,48,NULL,NULL),(350,'0.86',9,48,NULL,NULL),(351,'PlateThermoStandard',15,49,NULL,NULL),(352,'adherent (A)',14,49,NULL,NULL),(353,'expansion',13,49,NULL,NULL),(354,'-',18,49,NULL,NULL),(355,'45',1,49,NULL,NULL),(356,'10',3,49,NULL,NULL),(357,'10',5,49,NULL,NULL),(358,'PlateThermoStandard',15,50,NULL,NULL),(359,'adherent (A)',14,50,NULL,NULL),(360,'expansion',13,50,NULL,NULL),(361,'-',18,50,NULL,NULL),(362,'45',1,50,NULL,NULL),(363,'10',3,50,NULL,NULL),(364,'1',7,50,NULL,NULL),(365,'PlateThermoStandard',15,51,NULL,NULL),(366,'adherent (A)',14,51,NULL,NULL),(367,'expansion',13,51,NULL,NULL),(368,'-',18,51,NULL,NULL),(369,'1',11,51,NULL,NULL),(370,'10',3,51,NULL,NULL),(371,'45',2,51,NULL,NULL),(372,'PlateThermoStandard',15,52,NULL,NULL),(373,'adherent (A)',14,52,NULL,NULL),(374,'expansion',13,52,NULL,NULL),(375,'45',1,52,NULL,NULL),(376,'-',25,52,NULL,NULL),(377,'10',3,52,NULL,NULL),(378,'1',11,52,NULL,NULL),(379,'PlateThermoStandard',15,53,NULL,NULL),(380,'adherent (A)',14,53,NULL,NULL),(381,'generation',13,53,NULL,NULL),(382,'-',20,53,NULL,NULL),(383,'1',26,53,NULL,NULL),(384,'-',21,53,NULL,NULL),(385,'1',12,53,NULL,NULL),(386,'1',11,53,NULL,NULL),(387,'PlateThermoStandard',15,54,NULL,NULL),(388,'adherent (A)',14,54,NULL,NULL),(389,'generation',13,54,NULL,NULL),(390,'10',1,54,NULL,NULL),(391,'1',11,54,NULL,NULL),(392,'1',12,54,NULL,NULL),(393,'1',26,54,NULL,NULL),(394,'-',20,54,NULL,NULL),(395,'-',21,54,NULL,NULL),(396,'PlateThermoStandard',15,55,NULL,NULL),(397,'adherent (A)',14,55,NULL,NULL),(398,'generation',13,55,NULL,NULL),(399,'10',1,55,NULL,NULL),(400,'1',11,55,NULL,NULL),(401,'1',12,55,NULL,NULL),(402,'1',26,55,NULL,NULL),(403,'-',20,55,NULL,NULL),(404,'-',21,55,NULL,NULL),(405,'PlateThermoStandard',15,56,NULL,NULL),(406,'adherent (A)',14,56,NULL,NULL),(407,'generation',13,56,NULL,NULL),(408,'10',1,56,NULL,NULL),(409,'1',11,56,NULL,NULL),(410,'1',12,56,NULL,NULL),(411,'1',26,56,NULL,NULL),(412,'-',20,56,NULL,NULL),(413,'-',21,56,NULL,NULL),(414,'PlateThermoStandard',15,57,NULL,NULL),(415,'adherent (A)',14,57,NULL,NULL),(416,'generation',13,57,NULL,NULL),(417,'10',1,57,NULL,NULL),(418,'1',11,57,NULL,NULL),(419,'1',12,57,NULL,NULL),(420,'1',26,57,NULL,NULL),(421,'-',20,57,NULL,NULL),(422,'-',21,57,NULL,NULL);
/*!40000 ALTER TABLE `condition_has_feature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `condition_protocol`
--

DROP TABLE IF EXISTS `condition_protocol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `condition_protocol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protocol_name` varchar(255) DEFAULT NULL,
  `creation_date_time` datetime NOT NULL,
  `file_name` varchar(100) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `protocol_name_UNIQUE` (`protocol_name`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `condition_protocol`
--

LOCK TABLES `condition_protocol` WRITE;
/*!40000 ALTER TABLE `condition_protocol` DISABLE KEYS */;
INSERT INTO `condition_protocol` VALUES (1,'ISCOVE\'S 10% 10 cm dish','2014-02-26 13:25:48','',''),(2,'RPMI 10% 10 cm dish','2014-02-26 13:47:04','',''),(3,'MEM 10% 10 cm dish','2014-02-26 13:47:38','',''),(4,'DMEM-F12 20% 10 cm dish','2014-02-26 13:48:16','',''),(5,'DMEM 10% 10 cm dish','2014-02-26 13:48:49','',''),(6,'F12 10% 10 cm dish','2014-02-26 13:49:38','',''),(7,'MEM 10% + NEAA 1% 10 cm dish','2014-02-26 13:50:24','',''),(8,'DMEM 5% - 10 cm dish','2014-02-26 13:55:55','',''),(9,'DMEM-F12 10% - 10 cm dish','2014-02-26 13:56:35','',''),(10,'RMPI 10% + INS - 10 cm dish','2014-02-26 13:58:08','',''),(11,'DMEM 15% - 10 cm dish','2014-02-26 13:58:46','',''),(12,'HYBRICARE 10% + EGF - 10 cm dish','2014-02-26 14:04:47','',''),(13,'DMEM-F12 10% + NaPyr','2014-02-26 14:06:01','',''),(14,'DMEM-F12 10% + INS - 10 cm dish','2014-02-26 14:35:57','',''),(15,'DMEM-F12 10% + EGF - 10 cm dish','2014-02-26 14:40:05','',''),(16,'DMEM-F12 10% + HYDROCORTISONE','2014-02-26 14:41:04','',''),(17,'DMEM-F12 10% + INS + EGF + HYDROCORTISONE - 10 cm dish','2014-02-26 14:41:53','',''),(18,'McCOY\'S 10% - 10 cm dish','2014-02-26 14:42:54','',''),(19,'RPMI-F12 10% - 10 cm dish','2014-02-26 14:43:46','',''),(20,'DMEM-F12 5% - 10 cm dish','2014-02-26 14:46:26','',''),(21,'MEM 2+TRANSFERRIN - 10 cm dish','2014-02-26 14:48:50','',''),(22,'MEM 2+NAS - 10 cm dish','2014-02-26 14:50:05','',''),(23,'MEM 2+INSULIN - 10 cm dish','2014-02-26 14:50:51','',''),(24,'MEM 2+HYDROCORTISONE','2014-02-26 14:51:30','',''),(25,'MEM 8%  - 10 cm dish','2014-02-26 14:52:31','',''),(26,'L15 10% - 10 cm dish','2014-02-26 14:54:15','',''),(27,'ISCOVE\'S 10% FREEZE - 10 cm dish','2014-02-26 15:32:58','',''),(28,'RPMI 10% FREEZE - 10 cm dish','2014-02-26 15:33:40','',''),(29,'MEM 10% FREEZE - 10 cm dish','2014-02-26 15:34:22','',''),(30,'DMEM-F12 20% FREEZE - 10 cm dish','2014-02-26 15:35:11','',''),(31,'DMEM 10% FREEZE - 10 cm dish','2014-02-26 15:35:58','',''),(32,'F12 10% FREEZE - 10 cm dish','2014-02-26 15:40:23','',''),(33,'MEM 10% + NEAA 1% FREEZE - 10 cm dish','2014-02-26 15:41:20','',''),(34,'DMEM 5% FREEZE - 10 cm dish','2014-02-26 15:42:38','',''),(35,'DMEM-F12 10% FREEZE - 10 cm dish','2014-02-26 15:43:53','',''),(36,'RPMI 10% + INS FREEZE - 10 cm dish','2014-02-26 15:45:58','',''),(37,'DMEM 15% FREEZE - 10 cm dish','2014-02-26 15:47:02','',''),(38,'HYBRICARE 10% + EGF FREEZE - 10 cm dish','2014-02-26 15:48:19','',''),(39,'DMEM-F12 10% + NaPyr FREEZE - 10 cm dish','2014-02-26 15:49:29','',''),(40,'DMEM-F12 10% + INS FREEZE - 10 cm dish','2014-02-26 15:51:03','',''),(41,'DMEM-F12 10% + EGF FREEZE - 10 cm dish','2014-02-26 15:52:15','',''),(42,'DMEM-F12 10% + HYDROCORTISONE FREEZE - 10 cm dish','2014-02-26 15:53:13','',''),(43,'DMEM-F12 10% + INS + EGF + HYDROCORTISONE FREEZE - 10 cm dish','2014-02-26 15:54:52','',''),(44,'McCOY\'S 10% FREEZE - 10 cm dish','2014-02-26 15:57:17','',''),(45,'RPMI-F12 10% FREEZE - 10 cm dish','2014-02-26 15:58:03','',''),(46,'DMEM-F12 5% FREEZE - 10 cm dish','2014-02-26 15:58:55','',''),(47,'MEM 2+TRANSFERRIN FREEZE - 10 cm dish','2014-02-26 15:59:41','',''),(48,'MEM 2+NAS FREEZE - 10 cm dish','2014-02-26 16:01:09','',''),(49,'MEM 2+INSULIN FREEZE - 10 cm dish','2014-02-26 16:02:09','',''),(50,'MEM 2+HYDROCORTISONE FREEZE - 10 cm dish','2014-02-26 16:02:50','',''),(51,'MEM 8% FREEZE - 10 cm dish','2014-02-26 16:03:27','',''),(52,'L15 10% FREEZE - 10 cm dish','2014-02-26 16:04:04','',''),(53,'Generation Protocol 1','2014-02-27 10:49:34','',''),(54,'Generation Protocol 2 serum 10% - 10 cm dish','2014-02-27 10:50:33','',''),(55,'Generation Protocol 3 serum 10% - 10 cm dish','2014-02-27 10:51:09','',''),(56,'Generation Protocol 4 serum 10% - 10 cm dish','2014-02-27 10:51:42','',''),(57,'Generation Protocol 5 serum 10% - 10 cm dish','2014-02-27 10:52:10','','');
/*!40000 ALTER TABLE `condition_protocol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `condition_protocol_element`
--

DROP TABLE IF EXISTS `condition_protocol_element`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `condition_protocol_element` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` longtext,
  `condition_protocol_element_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `CellLineApp_conditionprotocolelement_7be91bc9` (`condition_protocol_element_id`),
  CONSTRAINT `conditionProtocolElement_id_refs_id_e6fcf43` FOREIGN KEY (`condition_protocol_element_id`) REFERENCES `condition_protocol_element` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `condition_protocol_element`
--

LOCK TABLES `condition_protocol_element` WRITE;
/*!40000 ALTER TABLE `condition_protocol_element` DISABLE KEYS */;
INSERT INTO `condition_protocol_element` VALUES (1,'Nutrients and chemical',NULL,NULL),(2,'Hormones/growth factors',NULL,NULL),(3,'Antibiotics',NULL,NULL),(4,'Serum',NULL,NULL),(5,'Media',NULL,NULL),(6,'DMSO',NULL,1),(7,'NEEA',NULL,2),(8,'Insulin',NULL,2),(9,'NaPyr',NULL,2),(10,'HydroCortisone',NULL,2),(11,'Trasnferrin',NULL,2),(12,'NAS',NULL,2),(13,'PS',NULL,3),(14,'Gentamicin',NULL,3),(15,'FBS',NULL,4),(16,'CALF',NULL,4),(17,'ISCOVE\'S',NULL,5),(18,'RPMI',NULL,5),(19,'MEM',NULL,5),(21,'F12',NULL,5),(22,'DMEM',NULL,5),(23,'HYBRICARE',NULL,5),(24,'McCOY\'S',NULL,5),(26,'L15',NULL,5),(27,'EGF',NULL,2),(28,'Glutammin',NULL,1),(29,'Fungizone',NULL,3);
/*!40000 ALTER TABLE `condition_protocol_element` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `conditions_has_experiments`
--

DROP TABLE IF EXISTS `conditions_has_experiments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `conditions_has_experiments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `end_time` datetime NOT NULL,
  `start_time` datetime NOT NULL,
  `experiment_in_vitro_id` int(11) NOT NULL,
  `condition_configuration_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_Condition_configuration_details_CellLineApp_experimentinvi1` (`experiment_in_vitro_id`),
  KEY `fk_Conditions_has_experiments_condition_configuration1` (`condition_configuration_id`),
  CONSTRAINT `fk_Condition_configuration_details_CellLineApp_experimentinvi1` FOREIGN KEY (`experiment_in_vitro_id`) REFERENCES `experiment_in_vitro` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_Conditions_has_experiments_condition_configuration1` FOREIGN KEY (`condition_configuration_id`) REFERENCES `condition_configuration` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conditions_has_experiments`
--

LOCK TABLES `conditions_has_experiments` WRITE;
/*!40000 ALTER TABLE `conditions_has_experiments` DISABLE KEYS */;
/*!40000 ALTER TABLE `conditions_has_experiments` ENABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'permission','auth','permission'),(2,'group','auth','group'),(3,'user','auth','user'),(4,'content type','contenttypes','contenttype'),(5,'session','sessions','session'),(6,'site','sites','site'),(7,'log entry','admin','logentry'),(8,'url handler','CellLineApp','urlhandler'),(9,'cancer research group','CellLineApp','cancerresearchgroup'),(10,'institution','CellLineApp','institution'),(11,'cell line users','CellLineApp','celllineusers'),(12,'condition protocol type','CellLineApp','conditionprotocoltype'),(13,'condition protocol element','CellLineApp','conditionprotocolelement'),(14,'condition configuration','CellLineApp','conditionconfiguration'),(15,'condition feature','CellLineApp','conditionfeature'),(16,'condition protocol_has_ feature','CellLineApp','conditionprotocol_has_feature'),(17,'condition_has_ feature','CellLineApp','condition_has_feature'),(18,'request','CellLineApp','request'),(19,'aliquots','CellLineApp','aliquots'),(20,'aliquots_has_ request','CellLineApp','aliquots_has_request'),(21,'expansion event','CellLineApp','expansionevent'),(22,'cells','CellLineApp','cells'),(23,'time','CellLineApp','time'),(24,'cell details','CellLineApp','celldetails'),(25,'experiment event','CellLineApp','experimentevent'),(26,'experiment in vitro','CellLineApp','experimentinvitro'),(27,'gen i d_archive','CellLineApp','genid_archive'),(28,'gen i d_generation','CellLineApp','genid_generation'),(29,'gen i d_parte1_generation','CellLineApp','genid_parte1_generation'),(30,'gen i d_parte2_generation','CellLineApp','genid_parte2_generation'),(31,'gen i d_letters_generation','CellLineApp','genid_letters_generation'),(32,'cult cond list_ name type','CellLineApp','cultcondlist_nametype'),(33,'plate number','CellLineApp','platenumber'),(34,'plate name','CellLineApp','platename'),(35,'archive table','CellLineApp','archivetable'),(36,'las_auth_session','LASAuth','lasauthsession'),(37,'nonce','piston','nonce'),(38,'resource','piston','resource'),(39,'consumer','piston','consumer'),(40,'token','piston','token');
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
INSERT INTO `django_session` VALUES ('24d713f2cae52d6e8737f2277e420175','NzVmZDg4OTNjNjEzMTU4NzhmMDk5Y2JhZjljMzk5MTBmNDk0Zjg1NzqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZFUbTEFTQXV0aC5hdXRoLkxBU0F1dGhCYWNrZW5kVQ1fYXV0aF91c2VyX2lkigEB\ndS4=\n','2014-03-13 10:52:10');
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
INSERT INTO `django_site` VALUES (1,'example.com','example.com');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliminated_details`
--

DROP TABLE IF EXISTS `eliminated_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `eliminated_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `amount` int(11) NOT NULL,
  `events_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_eliminated_details_events1` (`events_id`),
  CONSTRAINT `fk_eliminated_details_events1` FOREIGN KEY (`events_id`) REFERENCES `events` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliminated_details`
--

LOCK TABLES `eliminated_details` WRITE;
/*!40000 ALTER TABLE `eliminated_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `eliminated_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `events` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_time_event` datetime NOT NULL,
  `cellline_users_id` int(11) NOT NULL,
  `type_event_id` int(11) NOT NULL,
  `cell_details_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_events_cellline_users1_idx` (`cellline_users_id`),
  KEY `fk_events_type_event1_idx` (`type_event_id`),
  KEY `fk_events_cell_details1` (`cell_details_id`),
  CONSTRAINT `fk_events_cellline_users1` FOREIGN KEY (`cellline_users_id`) REFERENCES `auth_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_events_type_event1` FOREIGN KEY (`type_event_id`) REFERENCES `type_event` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_events_cell_details1` FOREIGN KEY (`cell_details_id`) REFERENCES `cell_details` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--

LOCK TABLES `events` WRITE;
/*!40000 ALTER TABLE `events` DISABLE KEYS */;
/*!40000 ALTER TABLE `events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `expansion_details`
--

DROP TABLE IF EXISTS `expansion_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `expansion_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `events_id` int(11) NOT NULL,
  `input_area` int(11) NOT NULL,
  `reduction_factor` int(11) NOT NULL DEFAULT '1',
  `output_area` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_expansion_details_events1_idx` (`events_id`),
  CONSTRAINT `fk_expansion_details_events1` FOREIGN KEY (`events_id`) REFERENCES `events` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expansion_details`
--

LOCK TABLES `expansion_details` WRITE;
/*!40000 ALTER TABLE `expansion_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `expansion_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `experiment_details`
--

DROP TABLE IF EXISTS `experiment_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `experiment_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `events_id` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `events_id_UNIQUE` (`events_id`),
  KEY `fk_experiment_details_events1_idx` (`events_id`),
  CONSTRAINT `fk_experiment_details_events1` FOREIGN KEY (`events_id`) REFERENCES `events` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `experiment_details`
--

LOCK TABLES `experiment_details` WRITE;
/*!40000 ALTER TABLE `experiment_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `experiment_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `experiment_in_vitro`
--

DROP TABLE IF EXISTS `experiment_in_vitro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `experiment_in_vitro` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `genID` varchar(26) NOT NULL,
  `experiment_details_id` int(11) NOT NULL,
  `cells_id` int(11) NOT NULL,
  `barcode_container` varchar(45) DEFAULT NULL,
  `position` varchar(45) DEFAULT NULL,
  `is_exausted` tinyint(1) DEFAULT '0',
  `is_available` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `fk_CellLineApp_experimentinvitro_CellLineApp_experimentevent1` (`experiment_details_id`),
  KEY `fk_experiment_in_vitro_cells1` (`cells_id`),
  CONSTRAINT `fk_CellLineApp_experimentinvitro_CellLineApp_experimentevent1` FOREIGN KEY (`experiment_details_id`) REFERENCES `experiment_details` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_experiment_in_vitro_cells1` FOREIGN KEY (`cells_id`) REFERENCES `cells` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `experiment_in_vitro`
--

LOCK TABLES `experiment_in_vitro` WRITE;
/*!40000 ALTER TABLE `experiment_in_vitro` DISABLE KEYS */;
/*!40000 ALTER TABLE `experiment_in_vitro` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `institution`
--

DROP TABLE IF EXISTS `institution`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `institution` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `institution`
--

LOCK TABLES `institution` WRITE;
/*!40000 ALTER TABLE `institution` DISABLE KEYS */;
INSERT INTO `institution` VALUES (1,'IRCC');
/*!40000 ALTER TABLE `institution` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `instrument`
--

DROP TABLE IF EXISTS `instrument`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `instrument` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `code` int(11) DEFAULT NULL,
  `manufacturer` varchar(45) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `instrument`
--

LOCK TABLES `instrument` WRITE;
/*!40000 ALTER TABLE `instrument` DISABLE KEYS */;
/*!40000 ALTER TABLE `instrument` ENABLE KEYS */;
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
  KEY `las_auth_session_25fa6905` (`django_session_key`),
  KEY `las_auth_session_72c09dd4` (`login_expire_date`),
  CONSTRAINT `django_session_key_refs_session_key_57a5cc49` FOREIGN KEY (`django_session_key`) REFERENCES `django_session` (`session_key`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `las_auth_session`
--

LOCK TABLES `las_auth_session` WRITE;
/*!40000 ALTER TABLE `las_auth_session` DISABLE KEYS */;
INSERT INTO `las_auth_session` VALUES ('920886da6fadb6a81a2d93af7554a34a','24d713f2cae52d6e8737f2277e420175','2014-02-26 10:43:28','/',1);
/*!40000 ALTER TABLE `las_auth_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `measure_details`
--

DROP TABLE IF EXISTS `measure_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `measure_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `events_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_measure_details_events1` (`events_id`),
  CONSTRAINT `fk_measure_details_events1` FOREIGN KEY (`events_id`) REFERENCES `events` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `measure_details`
--

LOCK TABLES `measure_details` WRITE;
/*!40000 ALTER TABLE `measure_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `measure_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `measure_event_has_measure_type`
--

DROP TABLE IF EXISTS `measure_event_has_measure_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `measure_event_has_measure_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` float DEFAULT NULL,
  `datasheet` varchar(45) DEFAULT NULL,
  `measure_details_id` int(11) NOT NULL,
  `measure_id` int(11) NOT NULL,
  `experiment_in_vitro_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_measure_event_has_measure_measure_event1` (`measure_details_id`),
  KEY `fk_measure_event_has_measure_measure1` (`measure_id`),
  KEY `fk_measure_event_has_measure_type_experiment_in_vitro1` (`experiment_in_vitro_id`),
  CONSTRAINT `fk_measure_event_has_measure_measure_event1` FOREIGN KEY (`measure_details_id`) REFERENCES `measure_details` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_measure_event_has_measure_measure1` FOREIGN KEY (`measure_id`) REFERENCES `measure_type` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_measure_event_has_measure_type_experiment_in_vitro1` FOREIGN KEY (`experiment_in_vitro_id`) REFERENCES `experiment_in_vitro` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `measure_event_has_measure_type`
--

LOCK TABLES `measure_event_has_measure_type` WRITE;
/*!40000 ALTER TABLE `measure_event_has_measure_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `measure_event_has_measure_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `measure_type`
--

DROP TABLE IF EXISTS `measure_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `measure_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `unity_measure` varchar(45) DEFAULT NULL,
  `instrument_id` int(11) NOT NULL,
  `cell_destroy` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ind` (`name`,`unity_measure`,`instrument_id`,`cell_destroy`),
  KEY `fk_measure_instrument1` (`instrument_id`),
  CONSTRAINT `fk_measure_instrument1` FOREIGN KEY (`instrument_id`) REFERENCES `instrument` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `measure_type`
--

LOCK TABLES `measure_type` WRITE;
/*!40000 ALTER TABLE `measure_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `measure_type` ENABLE KEYS */;
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
-- Table structure for table `type_event`
--

DROP TABLE IF EXISTS `type_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `type_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type_name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `type_name_UNIQUE` (`type_name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `type_event`
--

LOCK TABLES `type_event` WRITE;
/*!40000 ALTER TABLE `type_event` DISABLE KEYS */;
INSERT INTO `type_event` VALUES (4,'archive'),(1,'elimination'),(3,'expansion'),(5,'experiment'),(6,'measurement'),(2,'selection');
/*!40000 ALTER TABLE `type_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `urls_handler`
--

DROP TABLE IF EXISTS `urls_handler`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `urls_handler` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `url` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `urls_handler`
--

LOCK TABLES `urls_handler` WRITE;
/*!40000 ALTER TABLE `urls_handler` DISABLE KEYS */;
INSERT INTO `urls_handler` VALUES (1,'biobank','http://devircc.polito.it/biobank'),(2,'storage','http://devircc.polito.it/storage'),(3,'annotations','http://skylark.polito.it:8000');
/*!40000 ALTER TABLE `urls_handler` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-02-27 11:09:20
