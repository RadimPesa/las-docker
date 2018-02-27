-- MySQL dump 10.13  Distrib 5.5.40, for debian-linux-gnu (x86_64)
--
-- Host: 192.168.122.9    Database: lasauthserver
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
-- Table structure for table `loginmanager_activity`
--

DROP TABLE IF EXISTS `loginmanager_activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loginmanager_activity` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) NOT NULL,
  `father_activity_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `loginmanager_activity_ad5ccc71` (`father_activity_id`),
  CONSTRAINT `father_activity_id_refs_id_f010a065` FOREIGN KEY (`father_activity_id`) REFERENCES `loginmanager_activity` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loginmanager_activity`
--

LOCK TABLES `loginmanager_activity` WRITE;
/*!40000 ALTER TABLE `loginmanager_activity` DISABLE KEYS */;
INSERT INTO `loginmanager_activity` VALUES (1,'Manage Samples',NULL),(2,'Molecular Analysis',NULL),(3,'Facilities',NULL),(4,'In Vivo Experimentation',NULL),(5,'In Vitro Experimentation',NULL),(6,'Biobanking',NULL),(7,'Transfer',1),(8,'Split',1),(9,'Perform QC/QA',1),(10,'Derive',1),(11,'Kits and Protocols',1),(12,'Real-Time PCR',2),(13,'Sanger Sequencing',2),(15,'IHC',2),(16,'Western blots',2),(17,'Beaming',2),(18,'MicroArray',2),(19,'Review Experiments',4),(20,'Implants',4),(21,'Explants',4),(22,'Measures',4),(23,'Treatments',4),(24,'Cell line generator',5),(25,'Expansion',5),(26,'Experiments',1),(27,'Archive',5),(28,'Collection',6),(29,'Patients',6),(30,'Plan Samples Management',1),(32,'Retrieve Samples',1),(33,'Manage Mice',4),(34,'Repository',NULL),(35,'Manage Container',34),(39,'Manage Archive',34),(40,'Return Used Samples',34),(42,'Sequenom',2),(43,'Slide Preparation',1),(44,'Configuration',6),(45,'Configuration',4),(46,'Xeno Batch',4),(47,'Data querying and manipulation',NULL),(48,'Querying',47),(49,'Querying Admin',47),(50,'Data sharing',47),(51,'Mercuric',58),(52,'PI Activities',NULL),(53,'WG Management',52),(54,'NGS',2),(55,'DigitalPCR',2),(56,'Protocol Manager',5),(57,'Thawing',5),(58,'External Projects',NULL),(59,'Analysis',NULL),(60,'Randomizer',59),(61,'Write Formulas',59),(62,'Query Template',47);
/*!40000 ALTER TABLE `loginmanager_activity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loginmanager_lasvideo`
--

DROP TABLE IF EXISTS `loginmanager_lasvideo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loginmanager_lasvideo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `description` varchar(5000) NOT NULL,
  `url` varchar(200) NOT NULL,
  `rank` int(11) NOT NULL,
  `activity` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `loginmanager_lasvideo_eb4cc4e8` (`activity`),
  CONSTRAINT `activity_refs_id_6994d1c5` FOREIGN KEY (`activity`) REFERENCES `loginmanager_activity` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=76 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loginmanager_lasvideo`
--

LOCK TABLES `loginmanager_lasvideo` WRITE;
/*!40000 ALTER TABLE `loginmanager_lasvideo` DISABLE KEYS */;
INSERT INTO `loginmanager_lasvideo` VALUES (2,'Archive','','video/Xeno/archive.ogg',3,19),(3,'Change Status','','video/Xeno/changeStatus.ogg',2,33),(4,'Manage Groups','','video/Xeno/manageGroups.ogg',3,33),(5,'Finalize Treatments','','video/Xeno/finalizeTreat.ogg',2,23),(6,'Ongoing','','video/Xeno/ongoing.ogg',2,19),(8,'Create Treatments','','video/Xeno/browseCreateTreats.ogg',1,23),(9,'Implant Xenografts','','video/Xeno/implant.ogg',1,20),(10,'Explant Xenografts','','video/Xeno/explant.ogg',1,21),(11,'Register new animal','Register new animal','video/Xeno/Register.ogv',1,33),(13,'Review','','video/Xeno/review.ogg',1,19),(18,'Return container','Return container','video/Storage/Return.ogv',1,40),(23,'New kit type','','video/Biobank/Kit_type_new.ogg',1,11),(24,'New Kit','','video/Biobank/Kit_new.ogg',2,11),(25,'Assign aliquot to existing collection','Assign aliquot to existing collection','video/Biobank/Collect_arch_assign_to_exist.ogg',3,28),(26,'Collect fresh tissue','Collect fresh tissue','video/Biobank/Collection_fresh_tissue.ogv',1,28),(27,'New archive collection','New archive collection','video/Biobank/Collect_arch_new_collection.ogg',2,28),(28,'Plan derivation','Plan derivation','video/Biobank/Plan_derivation.ogv',1,10),(29,'Derivation 1 - Select Aliquots','Derivation 1 - Select Aliquots','video/Biobank/Derivation_select.ogv',2,10),(30,'Derivation 2 - Kit','','video/Biobank/Derivation_2_kit.ogg',3,10),(31,'Derivation 3 - Measures','Derivation 3 - Measures','video/Biobank/Derivation_3_measure.ogg',4,10),(32,'Derivation 4 - Create derivatives','Derivation 4 - Create derivatives','video/Biobank/Derivation_create_derivatives.ogv',5,10),(33,'Plan Split','','video/Biobank/Split_plan.ogg',1,8),(34,'Execute split','','video/Biobank/Split.ogg',2,8),(35,'Plan Transfer','Plan Transfer','video/Biobank/Plan_transfer.ogv',1,7),(36,'Send Transfer','Send Transfer','video/Biobank/Transfer_send.ogv',2,7),(37,'Receive Transfer','Receive Transfer','video/Biobank/Transfer_receive.ogv',3,7),(38,'Plan Experiment','','video/Biobank/Experiment_plan.ogg',1,26),(39,'Confirm Experiment','','video/Biobank/Experiment_confirm.ogg',2,26),(40,'Plan Revalue','Plan Revalue','video/Biobank/Plan_revalue.ogv',1,9),(41,'Execute Revalue','Execute Revalue','video/Biobank/Revalue.ogv',1,9),(42,'Plan Retrieve','','video/Biobank/Retrieve_plan.ogg',1,32),(43,'Execute Retrieve','','video/Biobank/Retrieve_execute.ogg',1,32),(44,'Patient','','video/Biobank/Patient.ogg',1,29),(45,'Manage controlled vocabulary','Manage controlled vocabulary','/video/Xeno/Xeno_Admin.ogv',1,45),(46,'Manage controlled vocabulary','Manage controlled vocabulary','/video/Biobank/Biobank_Admin.ogv',1,44),(47,'Archive free container','Archive free container','/video/Storage/Archive_free_container.ogv',2,39),(48,'Move container','Move container','/video/Storage/Move_container.ogv',1,39),(49,'Change container features','Change container features','/video/Storage/Change_container_features.ogv',4,35),(50,'New container geometry','New container geometry','/video/Storage/New_geometry.ogv',5,35),(51,'Load container – Single-container mode','Load container – Single-container mode','/video/Storage/New_single_container.ogv',2,35),(53,'Load container – Batch mode','Load container – Batch mode','/video/Storage/Load_batch.ogv',3,35),(54,'New container type','New container type','/video/Storage/New_container_type.ogv',1,35),(55,'Weight','Weight','/video/Xeno/Weight.ogv',3,22),(56,'Observation','Observation','/video/Xeno/Observation.ogv',1,22),(57,'Tumor volume','Tumor volume','/video/Xeno/Volume.ogv',2,22),(58,'Tumor volume and weight','Tumor volume and weight','/video/Xeno/Volume_weight.ogv',4,22),(59,'Validate samples','Validate samples','/video/Sanger/Sanger_Validate.ogv',2,13),(60,'Validate samples','Validate samples','/video/RtPcr/RT_Validate.ogv',2,12),(61,'Simple query','Simple query','/video/Query/Query1.ogv',1,48),(62,'Define and use query template','Define and use query template','/video/Query/Templates.ogv',1,62),(63,'Execute slide preparation','Execute slide preparation','/video/Biobank/Execute_slides_preparation.ogv',2,43),(64,'Plan slide preparation','Plan slide preparation','/video/Biobank/Plan_slides_preparation.ogv',1,43),(65,'Create randomized groups','Create randomized groups','/video/Analysis/Randomizer.ogv',1,60),(66,'Plan experiment','Plan experiment','/video/RtPcr/Plan_rtpcr.ogv',1,12),(67,'Plan experiment','Plan experiment','/video/Sanger/Plan_sanger.ogv',1,13),(68,'Collection','Collection - Fresh tissue','/video/Mercuric/Mercuric.ogv',1,51),(69,'New protocol','New protocol','/video/CellLines/New_protocol.ogv',1,56),(70,'Plan experiment','Plan experiment','/video/Biobank/Plan_sequenom.ogv',1,42),(71,'Registration – Basic User','Registration – Basic User','/video/LASAuth/regUser.ogv',1,53),(72,'Registration – Principal Investigator','Registration – Principal Investigator','/video/LASAuth/regPI.ogv',2,53),(73,'Manage users and functionalities','Manage users and functionalities','/video/LASAuth/manageWG.ogv',3,53),(74,'New batch collection','New batch collection','/video/Biobank/Collection_batch.ogv',4,28),(75,'New cell line','New cell line','/video/Biobank/Collection_cell_lines.ogv',5,28);
/*!40000 ALTER TABLE `loginmanager_lasvideo` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-02-02 16:39:43
