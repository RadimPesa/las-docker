-- MySQL dump 10.13  Distrib 5.5.40, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: biobanca
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
-- Current Database: `biobanca`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `biobanca` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `biobanca`;

--
-- Table structure for table `aliquot`
--

DROP TABLE IF EXISTS `aliquot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquot` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `barcodeID` varchar(45) DEFAULT NULL,
  `uniqueGenealogyID` varchar(30) NOT NULL,
  `idSamplingEvent` int(11) NOT NULL,
  `idAliquotType` int(11) NOT NULL,
  `availability` tinyint(1) NOT NULL,
  `timesUsed` int(11) NOT NULL,
  `derived` tinyint(1) NOT NULL,
  `archiveDate` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniqueGenealogyID_UNIQUE` (`uniqueGenealogyID`),
  KEY `fk_Aliquots_AliquotType1` (`idAliquotType`),
  KEY `fk_Aliquots_SamplingEvents1` (`idSamplingEvent`),
  CONSTRAINT `fk_Aliquots_AliquotType1` FOREIGN KEY (`idAliquotType`) REFERENCES `aliquottype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_Aliquots_SamplingEvents1` FOREIGN KEY (`idSamplingEvent`) REFERENCES `samplingevent` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=137030 DEFAULT CHARSET=latin1;
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
  `barcodeID` varchar(45) DEFAULT NULL,
  `uniqueGenealogyID` varchar(30) NOT NULL,
  `idSamplingEvent` int(11) NOT NULL,
  `idAliquotType` int(11) NOT NULL,
  `availability` tinyint(1) NOT NULL,
  `timesUsed` int(11) NOT NULL,
  `derived` tinyint(1) NOT NULL,
  `archiveDate` date DEFAULT NULL,
  `username` varchar(30) NOT NULL,
  `_audit_id` int(11) NOT NULL AUTO_INCREMENT,
  `_audit_timestamp` datetime NOT NULL,
  `_audit_change_type` varchar(1) NOT NULL,
  PRIMARY KEY (`_audit_id`)
) ENGINE=InnoDB AUTO_INCREMENT=247682 DEFAULT CHARSET=latin1;
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
CREATE trigger audit_aliquot
before insert on aliquot_audit
for each row
begin
if new._audit_change_type= 'I' then
select id into @aliq_id
from aliquot
where aliquot.uniqueGenealogyID= new.uniqueGenealogyID;
set new.id=@aliq_id;
END if;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `aliquot_wg`
--

DROP TABLE IF EXISTS `aliquot_wg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquot_wg` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_aliquot` int(11) DEFAULT NULL,
  `WG_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_aliquot_wg_aliquot` (`id_aliquot`),
  KEY `fk_aliquot_wg_wg` (`WG_id`),
  CONSTRAINT `fk_aliquot_wg_aliquot` FOREIGN KEY (`id_aliquot`) REFERENCES `aliquot` (`id`),
  CONSTRAINT `fk_aliquot_wg_wg` FOREIGN KEY (`WG_id`) REFERENCES `tissue_wg` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=155909 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquot_wg`
--

LOCK TABLES `aliquot_wg` WRITE;
/*!40000 ALTER TABLE `aliquot_wg` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliquot_wg` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aliquotderivationschedule`
--

DROP TABLE IF EXISTS `aliquotderivationschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquotderivationschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idAliquot` int(11) NOT NULL,
  `idDerivationSchedule` int(11) NOT NULL,
  `idDerivedAliquotType` int(11) NOT NULL,
  `idDerivationProtocol` int(11) DEFAULT NULL,
  `idKit` int(11) DEFAULT NULL,
  `derivationExecuted` tinyint(1) NOT NULL,
  `operator` varchar(45) NOT NULL,
  `loadQuantity` double DEFAULT NULL,
  `volumeOutcome` double DEFAULT NULL,
  `failed` tinyint(1) DEFAULT NULL,
  `initialDate` date DEFAULT NULL,
  `measurementExecuted` tinyint(1) DEFAULT NULL,
  `aliquotExhausted` tinyint(1) DEFAULT NULL,
  `deleteTimestamp` datetime DEFAULT NULL,
  `deleteOperator` int(11) DEFAULT NULL,
  `validationTimestamp` datetime DEFAULT NULL,
  `notes` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_AliquotsDerivationSchedule_Aliquots1` (`idAliquot`),
  KEY `fk_AliquotsDerivationSchedule_DerivationSchedule1` (`idDerivationSchedule`),
  KEY `fk_AliquotDerivationSchedule_DerivationProtocol1` (`idDerivationProtocol`),
  KEY `fk_AliquotDerivationSchedule_Kit1` (`idKit`),
  KEY `fk_AliquotsDerivationSchedule_AliquotType1` (`idDerivedAliquotType`),
  KEY `fk_aliquotderivationschedule_1` (`deleteOperator`),
  CONSTRAINT `fk_aliquotderivationschedule_1` FOREIGN KEY (`deleteOperator`) REFERENCES `auth_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_AliquotDerivationSchedule_AliquotType1` FOREIGN KEY (`idDerivedAliquotType`) REFERENCES `aliquottype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_AliquotDerivationSchedule_DerivationProtocol1` FOREIGN KEY (`idDerivationProtocol`) REFERENCES `derivationprotocol` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_AliquotDerivationSchedule_Kit1` FOREIGN KEY (`idKit`) REFERENCES `kit` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_AliquotsDerivationSchedule_Aliquots1` FOREIGN KEY (`idAliquot`) REFERENCES `aliquot` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_AliquotsDerivationSchedule_DerivationSchedule1` FOREIGN KEY (`idDerivationSchedule`) REFERENCES `derivationschedule` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=10911 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquotderivationschedule`
--

LOCK TABLES `aliquotderivationschedule` WRITE;
/*!40000 ALTER TABLE `aliquotderivationschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliquotderivationschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aliquotderivationschedule_audit`
--

DROP TABLE IF EXISTS `aliquotderivationschedule_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquotderivationschedule_audit` (
  `id` int(11) NOT NULL,
  `idAliquot` int(11) NOT NULL,
  `idDerivationSchedule` int(11) NOT NULL,
  `idDerivedAliquotType` int(11) NOT NULL,
  `idDerivationProtocol` int(11) DEFAULT NULL,
  `idKit` int(11) DEFAULT NULL,
  `derivationExecuted` tinyint(1) NOT NULL,
  `operator` varchar(45) NOT NULL,
  `loadQuantity` double DEFAULT NULL,
  `volumeOutcome` double DEFAULT NULL,
  `failed` tinyint(1) DEFAULT NULL,
  `initialDate` date DEFAULT NULL,
  `measurementExecuted` tinyint(1) DEFAULT NULL,
  `aliquotExhausted` tinyint(1) DEFAULT NULL,
  `deleteTimestamp` datetime DEFAULT NULL,
  `deleteOperator` int(11) DEFAULT NULL,
  `validationTimestamp` datetime DEFAULT NULL,
  `notes` varchar(150) DEFAULT NULL,
  `username` varchar(30) NOT NULL,
  `_audit_id` int(11) NOT NULL AUTO_INCREMENT,
  `_audit_timestamp` datetime NOT NULL,
  `_audit_change_type` varchar(1) NOT NULL,
  PRIMARY KEY (`_audit_id`)
) ENGINE=InnoDB AUTO_INCREMENT=31646 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquotderivationschedule_audit`
--

LOCK TABLES `aliquotderivationschedule_audit` WRITE;
/*!40000 ALTER TABLE `aliquotderivationschedule_audit` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliquotderivationschedule_audit` ENABLE KEYS */;
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
CREATE trigger audit_derivation
before insert on aliquotderivationschedule_audit
for each row
begin
if new._audit_change_type= 'I' then
select id into @id
from aliquotderivationschedule
where aliquotderivationschedule.idAliquot= new.idAliquot and aliquotderivationschedule.idDerivationSchedule=new.idDerivationSchedule and aliquotderivationschedule.idDerivedAliquotType=new.idDerivedAliquotType and derivationExecuted=0 and deleteTimestamp is null;
set new.id=@id;
END if;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `aliquotexperiment`
--

DROP TABLE IF EXISTS `aliquotexperiment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquotexperiment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idAliquot` int(11) NOT NULL,
  `idExperiment` int(11) NOT NULL,
  `idExperimentSchedule` int(11) DEFAULT NULL,
  `takenValue` double NOT NULL,
  `remainingValue` double NOT NULL,
  `operator` varchar(45) NOT NULL,
  `experimentDate` date NOT NULL,
  `aliquotExhausted` tinyint(1) DEFAULT NULL,
  `confirmed` tinyint(1) NOT NULL,
  `notes` varchar(150) DEFAULT NULL,
  `deleteTimestamp` datetime DEFAULT NULL,
  `deleteOperator` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_AliquotExperiment_Aliquot` (`idAliquot`),
  KEY `fk_AliquotExperiment_Experiment` (`idExperiment`),
  KEY `fk_aliquotexperiment_1` (`idExperimentSchedule`),
  KEY `fk_aliquotexperiment_2` (`deleteOperator`),
  CONSTRAINT `fk_aliquotexperiment_1` FOREIGN KEY (`idExperimentSchedule`) REFERENCES `experimentschedule` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_aliquotexperiment_2` FOREIGN KEY (`deleteOperator`) REFERENCES `auth_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_AliquotExperiment_Aliquot` FOREIGN KEY (`idAliquot`) REFERENCES `aliquot` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_AliquotExperiment_Experiment` FOREIGN KEY (`idExperiment`) REFERENCES `experiment` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=7030 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquotexperiment`
--

LOCK TABLES `aliquotexperiment` WRITE;
/*!40000 ALTER TABLE `aliquotexperiment` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliquotexperiment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aliquotfeature`
--

DROP TABLE IF EXISTS `aliquotfeature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquotfeature` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idAliquot` int(11) NOT NULL,
  `idFeature` int(11) NOT NULL,
  `value` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_AliquotsFeature_Feature1` (`idFeature`),
  KEY `fk_AliquotsFeature_Aliquots1` (`idAliquot`),
  CONSTRAINT `fk_AliquotsFeature_Aliquots1` FOREIGN KEY (`idAliquot`) REFERENCES `aliquot` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_AliquotsFeature_Feature1` FOREIGN KEY (`idFeature`) REFERENCES `feature` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=233631 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquotfeature`
--

LOCK TABLES `aliquotfeature` WRITE;
/*!40000 ALTER TABLE `aliquotfeature` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliquotfeature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aliquotpositionschedule`
--

DROP TABLE IF EXISTS `aliquotpositionschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquotpositionschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idAliquot` int(11) NOT NULL,
  `idPositionSchedule` int(11) NOT NULL,
  `positionExecuted` tinyint(1) NOT NULL,
  `notes` varchar(150) DEFAULT NULL,
  `deleteTimestamp` datetime DEFAULT NULL,
  `deleteOperator` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_AliquotPositionSchedule_Aliquot1` (`idAliquot`),
  KEY `fk_AliquotPositionSchedule_PositionSchedule1` (`idPositionSchedule`),
  KEY `fk_aliquotpositionschedule_1` (`deleteOperator`),
  CONSTRAINT `fk_aliquotpositionschedule_1` FOREIGN KEY (`deleteOperator`) REFERENCES `auth_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_AliquotPositionSchedule_Aliquot1` FOREIGN KEY (`idAliquot`) REFERENCES `aliquot` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_AliquotPositionSchedule_PositionSchedule1` FOREIGN KEY (`idPositionSchedule`) REFERENCES `positionschedule` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=536 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquotpositionschedule`
--

LOCK TABLES `aliquotpositionschedule` WRITE;
/*!40000 ALTER TABLE `aliquotpositionschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliquotpositionschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aliquotqualityschedule`
--

DROP TABLE IF EXISTS `aliquotqualityschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquotqualityschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idAliquot` int(11) NOT NULL,
  `idQualitySchedule` int(11) NOT NULL,
  `revaluationExecuted` tinyint(1) NOT NULL,
  `deleteTimestamp` datetime DEFAULT NULL,
  `deleteOperator` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_AliquotsDerivationSchedule_Aliquots1` (`idAliquot`),
  KEY `fk_AliquotsQualitySchedule_QualitySchedule1` (`idQualitySchedule`),
  KEY `fk_aliquotqualityschedule_1` (`deleteOperator`),
  CONSTRAINT `fk_aliquotqualityschedule_1` FOREIGN KEY (`deleteOperator`) REFERENCES `auth_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_AliquotsDerivationSchedule_Aliquots10` FOREIGN KEY (`idAliquot`) REFERENCES `aliquot` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_AliquotsQualitySchedule_QualitySchedule1` FOREIGN KEY (`idQualitySchedule`) REFERENCES `qualityschedule` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=413 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquotqualityschedule`
--

LOCK TABLES `aliquotqualityschedule` WRITE;
/*!40000 ALTER TABLE `aliquotqualityschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliquotqualityschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aliquotslideschedule`
--

DROP TABLE IF EXISTS `aliquotslideschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquotslideschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idAliquot` int(11) NOT NULL,
  `idSlideSchedule` int(11) NOT NULL,
  `idSamplingEvent` int(11) DEFAULT NULL,
  `idSlideProtocol` int(11) DEFAULT NULL,
  `operator` int(11) DEFAULT NULL,
  `aliquotExhausted` tinyint(1) DEFAULT NULL,
  `executionDate` date DEFAULT NULL,
  `executed` tinyint(1) NOT NULL,
  `notes` varchar(150) DEFAULT NULL,
  `deleteTimestamp` datetime DEFAULT NULL,
  `deleteOperator` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_aliquotSlideSchedule_1` (`idAliquot`),
  KEY `fk_aliquotSlideSchedule_2` (`idSlideSchedule`),
  KEY `fk_aliquotSlideSchedule_3` (`idSamplingEvent`),
  KEY `fk_aliquotSlideSchedule_4` (`idSlideProtocol`),
  CONSTRAINT `fk_aliquotSlideSchedule_1` FOREIGN KEY (`idAliquot`) REFERENCES `aliquot` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_aliquotSlideSchedule_2` FOREIGN KEY (`idSlideSchedule`) REFERENCES `slideschedule` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_aliquotSlideSchedule_3` FOREIGN KEY (`idSamplingEvent`) REFERENCES `samplingevent` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_aliquotSlideSchedule_4` FOREIGN KEY (`idSlideProtocol`) REFERENCES `slideprotocol` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquotslideschedule`
--

LOCK TABLES `aliquotslideschedule` WRITE;
/*!40000 ALTER TABLE `aliquotslideschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliquotslideschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aliquotsplitschedule`
--

DROP TABLE IF EXISTS `aliquotsplitschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquotsplitschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idAliquot` int(11) NOT NULL,
  `idSplitSchedule` int(11) NOT NULL,
  `idSamplingEvent` int(11) DEFAULT NULL,
  `splitExecuted` tinyint(1) NOT NULL,
  `deleteTimestamp` datetime DEFAULT NULL,
  `deleteOperator` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_AliquotsDerivationSchedule_Aliquots11` (`idAliquot`),
  KEY `fk_AliquotsSplitSchedule_QualitySchedule1` (`idSplitSchedule`),
  KEY `fk_SplitSchedule_SamplingEvent1` (`idSamplingEvent`),
  KEY `fk_aliquotsplitschedule_1` (`deleteOperator`),
  CONSTRAINT `fk_AliquotsDerivationSchedule_Aliquots11` FOREIGN KEY (`idAliquot`) REFERENCES `aliquot` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_aliquotsplitschedule_1` FOREIGN KEY (`deleteOperator`) REFERENCES `auth_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_AliquotsSplitSchedule_QualitySchedule1` FOREIGN KEY (`idSplitSchedule`) REFERENCES `splischedule` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_SplitSchedule_SamplingEvent1` FOREIGN KEY (`idSamplingEvent`) REFERENCES `samplingevent` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1137 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquotsplitschedule`
--

LOCK TABLES `aliquotsplitschedule` WRITE;
/*!40000 ALTER TABLE `aliquotsplitschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliquotsplitschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aliquottransferschedule`
--

DROP TABLE IF EXISTS `aliquottransferschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquottransferschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idAliquot` int(11) NOT NULL,
  `idTransfer` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_aliquottransferschedule_1` (`idAliquot`),
  KEY `fk_aliquottransferschedule_2` (`idTransfer`),
  CONSTRAINT `fk_aliquottransferschedule_1` FOREIGN KEY (`idAliquot`) REFERENCES `aliquot` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_aliquottransferschedule_2` FOREIGN KEY (`idTransfer`) REFERENCES `transfer` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquottransferschedule`
--

LOCK TABLES `aliquottransferschedule` WRITE;
/*!40000 ALTER TABLE `aliquottransferschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliquottransferschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aliquottype`
--

DROP TABLE IF EXISTS `aliquottype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquottype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `abbreviation` varchar(4) NOT NULL,
  `longName` varchar(20) NOT NULL,
  `type` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquottype`
--

LOCK TABLES `aliquottype` WRITE;
/*!40000 ALTER TABLE `aliquottype` DISABLE KEYS */;
INSERT INTO `aliquottype` VALUES (1,'VT','Viable','Original'),(2,'SF','Snap Frozen','Original'),(3,'RL','RNAlater','Original'),(4,'FF','Formalin Fixed','Block'),(5,'OF','OCTfrozen','Block'),(6,'CH','ChinaBlack','Block'),(7,'DNA','DNA','Derived'),(8,'RNA','RNA','Derived'),(9,'cDNA','Complementary DNA','Derived'),(10,'cRNA','Complementary RNA','Derived'),(11,'PL','Plasma','Original'),(12,'PX','PAXtube','Original'),(13,'FR','Frozen','Original'),(14,'FS','FrozenSediment','Original'),(15,'PS','ParaffinSection','Block'),(16,'OS','OCTSection','Block'),(17,'P','Protein','Derived');
/*!40000 ALTER TABLE `aliquottype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aliquottypeexperiment`
--

DROP TABLE IF EXISTS `aliquottypeexperiment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliquottypeexperiment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idExperiment` int(11) NOT NULL,
  `idAliquotType` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_AliquotTypeExperiment_AliquotType` (`idAliquotType`),
  KEY `fk_AliqTypeExp_Exp` (`idExperiment`),
  CONSTRAINT `fk_AliqTypeExp_Exp` FOREIGN KEY (`idExperiment`) REFERENCES `experiment` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_AliquotTypeExperiment_AliquotType` FOREIGN KEY (`idAliquotType`) REFERENCES `aliquottype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliquottypeexperiment`
--

LOCK TABLES `aliquottypeexperiment` WRITE;
/*!40000 ALTER TABLE `aliquottypeexperiment` DISABLE KEYS */;
INSERT INTO `aliquottypeexperiment` VALUES (1,1,9),(2,1,10),(3,2,7),(4,2,8),(5,3,7),(6,3,8),(7,3,9),(8,3,10),(9,4,4),(10,4,5),(11,5,1),(12,5,2),(13,5,3),(14,5,4),(15,5,5),(16,5,7),(17,5,8),(18,5,9),(19,5,10),(20,6,1),(21,6,2),(22,6,3),(23,6,4),(24,6,5),(25,6,7),(26,6,8),(27,6,9),(28,6,10),(33,8,1),(38,10,7),(39,10,8),(40,10,9),(41,10,10),(42,11,1);
/*!40000 ALTER TABLE `aliquottypeexperiment` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can add user',3,'add_user'),(5,'Can change user',3,'change_user'),(6,'Can delete user',3,'delete_user'),(7,'Can add group',2,'add_group'),(8,'Can change group',2,'change_group'),(9,'Can delete group',2,'delete_group'),(10,'Can add log entry',4,'add_logentry'),(11,'Can change log entry',4,'change_logentry'),(12,'Can delete log entry',4,'delete_logentry'),(13,'Can add content type',5,'add_contenttype'),(14,'Can change content type',5,'change_contenttype'),(15,'Can delete content type',5,'delete_contenttype'),(16,'Can add session',6,'add_session'),(17,'Can change session',6,'change_session'),(18,'Can delete session',6,'delete_session'),(19,'Can add site',7,'add_site'),(20,'Can change site',7,'change_site'),(21,'Can delete site',7,'delete_site'),(22,'Can add nonce',8,'add_nonce'),(23,'Can change nonce',8,'change_nonce'),(24,'Can delete nonce',8,'delete_nonce'),(25,'Can add resource',10,'add_resource'),(26,'Can change resource',10,'change_resource'),(27,'Can delete resource',10,'delete_resource'),(28,'Can add consumer',11,'add_consumer'),(29,'Can change consumer',11,'change_consumer'),(30,'Can delete consumer',11,'delete_consumer'),(31,'Can add token',9,'add_token'),(32,'Can change token',9,'change_token'),(33,'Can delete token',9,'delete_token'),(58,'Institutional Collection',53,'can_view_BBM_institutional_collection'),(59,'Collaboration Collection',53,'can_view_BBM_collaboration_collection'),(60,'Insert New Kit Type',53,'can_view_BBM_insert_new_kit_type'),(61,'Register New Kit',53,'can_view_BBM_register_new_kit'),(62,'Create New Protocol',53,'can_view_BBM_create_new_protocol'),(63,'Plan Derivation',53,'can_view_BBM_plan_derivation'),(64,'Select Aliquots And Protocols',53,'can_view_BBM_select_aliquots_and_protocols'),(65,'Select Kit',53,'can_view_BBM_select_kit'),(66,'Perform Qc Qa',53,'can_view_BBM_perform_QC_QA'),(67,'Create Derivatives',53,'can_view_BBM_create_derivatives'),(68,'Calculate Aliquot Values',53,'can_view_BBM_calculate_aliquot_values'),(69,'Plan Aliquots To Revalue',53,'can_view_BBM_plan_aliquots_to_revalue'),(70,'Revalue Aliquots',53,'can_view_BBM_revalue_aliquots'),(71,'File Saved',53,'can_view_BBM_file_saved'),(72,'Plan Aliquots To Split',53,'can_view_BBM_plan_aliquots_to_split'),(73,'Split Aliquots',53,'can_view_BBM_split_aliquots'),(74,'Plan Retrieval',53,'can_view_BBM_plan_retrieval'),(75,'Retrieve Aliquots',53,'can_view_BBM_retrieve_aliquots'),(76,'Plan Experiments',53,'can_view_BBM_plan_experiments'),(77,'Execute Experiments',53,'can_view_BBM_execute_experiments'),(78,'Plan Transfer',53,'can_view_BBM_plan_transfer'),(79,'Send Aliquots to Transfer',53,'can_view_BBM_send_aliquots'),(80,'Receive Aliquots to Transfer',53,'can_view_BBM_receive_aliquots'),(81,'Patients',53,'can_view_BBM_patients'),(82,'Plan slide preparation',53,'can_view_BBM_plan_aliquots_to_slide'),(83,'Execute slide preparation',53,'can_view_BBM_execute_slide_aliquots'),(84,'Biobank admin',53,'can_view_BBM_admin'),(85,'Mercuric', 53, 'can_view_BBM_mercuric');
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
) ENGINE=InnoDB AUTO_INCREMENT=9752 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clinicalfeature`
--

DROP TABLE IF EXISTS `clinicalfeature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clinicalfeature` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `measureUnit` varchar(20) DEFAULT NULL,
  `type` varchar(30) DEFAULT NULL,
  `idClinicalFeature` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_clinicalfeature_1` (`idClinicalFeature`),
  CONSTRAINT `fk_clinicalfeature_1` FOREIGN KEY (`idClinicalFeature`) REFERENCES `clinicalfeature` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=140 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clinicalfeature`
--

LOCK TABLES `clinicalfeature` WRITE;
/*!40000 ALTER TABLE `clinicalfeature` DISABLE KEYS */;
INSERT INTO `clinicalfeature` VALUES (1,'24-H urines','ml','Number',47),(3,'Notes','','',NULL),(4,'idCellLine','','Cellline',NULL),(5,'MTA','','Cellline',NULL),(6,'LotNumber','','Cellline',NULL),(7,'MycoplasmaPositive','','Cellline',NULL),(8,'RelatedFile','','Cellline',NULL),(40,'Anagraphics','','Level1',NULL),(41,'Laboratory data','','Level1',NULL),(42,'Patient treatments','','Level1',NULL),(43,'Disease history','','Level1',NULL),(44,'Molecular markers','','Level1',NULL),(45,'Pathological features','','Level1',NULL),(46,'Tumour markers','','Level2',41),(47,'Functional parameters','','Level2',41),(48,'Serological markers','','Level2',41),(49,'Year of birth','','Year',40),(50,'Gender','','RadioList',40),(51,'CEA','ng/ml','Number',46),(52,'CA125','U/ml','Number',46),(53,'CA19-9','U/ml','Number',46),(54,'CA15-3','U/ml','Number',46),(55,'TPA','ng/ml','Number',46),(56,'LDH','U/l','Number',46),(57,'Alpha-fetoprotein','ng/ml','Number',46),(58,'EBV','','RadioList',48),(59,'HBV','','RadioList',48),(60,'HCV','','RadioList',48),(61,'HIV','','RadioList',48),(62,'HPV','','RadioList',48),(63,'Treatments','','Level2',42),(64,'Sensitivity info','','Level2',42),(65,'Former/Previous','','Autocomplete',63),(66,'Ongoing','','Autocomplete',63),(67,'Scheduled/Planned','','Autocomplete',63),(68,'Sensitive to','','Autocomplete',64),(69,'Resistant to','','Autocomplete',64),(70,'Date of surgery','','Date',43),(71,'Date first diagnosis','','Date',43),(72,'Date diagnosis current collection','','Date',43),(73,'Death date','','Date',43),(74,'Date last follow up','','Date',43),(75,'Disease status at follow up','','List',43),(76,'IHC','','Level2',44),(77,'FISH','','Level2',44),(78,'Sequencing','','Level2',44),(79,'FISH value','','FISH',77),(80,'Sequencing value','','Sequencing',78),(81,'PR_R','','TextTumor',76),(82,'ER_R','','TextTumor',76),(83,'HER_R','','TextTumor',76),(84,'Other_R','','TextTumor',76),(85,'EMA_EMC_F0','','TextTumor',76),(86,'Prekeratin_EMC_F0','','TextTumor',76),(87,'CD10_EMC_F0','','TextTumor',76),(88,'TP53_EMC_F0','','TextTumor',76),(89,'ER_EMC_F0','','TextTumor',76),(90,'PR_EMC_F0','','TextTumor',76),(91,'Phosph-S6_EMC','','TextTumor',76),(92,'p53_EMC','','TextTumor',76),(93,'MSH6_EMC','','TextTumor',76),(94,'MLH1_EMC','','TextTumor',76),(95,'MSH2_EMC','','TextTumor',76),(96,'Desmin_US_F0','','TextTumor',76),(97,'ER_US_F0','','TextTumor',76),(98,'PR_US_F0','','TextTumor',76),(99,'Caldesmon_US_F0','','TextTumor',76),(100,'AlphaSMA_US_F0','','TextTumor',76),(101,'CD10_US_F0','','TextTumor',76),(102,'Vimentin_US_F0','','TextTumor',76),(103,'Cytokeratin_US_F0','','TextTumor',76),(104,'EMA_US_F0','','TextTumor',76),(105,'PDGFR-alpha US','','TextTumor',76),(106,'Phospho-S6 US','','TextTumor',76),(107,'PTEN US','','TextTumor',76),(108,'ERBB2 US','','TextTumor',76),(109,'VEGF US','','TextTumor',76),(110,'EGFR US','','TextTumor',76),(111,'Cytokeratin_OVC_F0','','TextTumor',76),(112,'Vimentin_OVC_F0','','TextTumor',76),(113,'Phosph-S6_OVC','','TextTumor',76),(114,'TP53_OVC_F0','','TextTumor',76),(115,'MSH6_OVC','','TextTumor',76),(116,'MLH1_OVC','','TextTumor',76),(117,'MSH2_OVC','','TextTumor',76),(118,'p53 positive','','TextTumor',76),(119,'Main features','','Level2',45),(120,'Other parameters','','Level2',45),(121,'Histological classification','','List',119),(122,'Histological grading','','List',119),(123,'Staging','','List',119),(124,'Location','','List',119),(125,'TNM','','TNM',119),(126,'Breslow','','TextTumor',120),(127,'Mitotic Index','','TextTumor',120),(128,'Ulceration','','TextTumor',120),(129,'Clarck','','TextTumor',120),(130,'Micro Macroscopic','','TextTumor',120),(131,'Number of Lnn','','TextTumor',120),(132,'Extracapsular Dissemination','','TextTumor',120),(133,'Satellites','','TextTumor',120),(134,'In Transit Metastasis','','TextTumor',120),(135,'Skin_Non Regional lnn','','TextTumor',120),(136,'Met_lungs','','TextTumor',120),(137,'Met_Others','','TextTumor',120),(138,'Distant Metastasis','','TextTumor',120),(139,'Met_Remarks','','TextTumor',120);
/*!40000 ALTER TABLE `clinicalfeature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clinicalfeaturecollectiontype`
--

DROP TABLE IF EXISTS `clinicalfeaturecollectiontype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clinicalfeaturecollectiontype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idClinicalFeature` int(11) NOT NULL,
  `idCollectionType` int(11) DEFAULT NULL,
  `value` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_clinicalfeaturecollectiontype_1` (`idClinicalFeature`),
  KEY `fk_clinicalfeaturecollectiontype_2` (`idCollectionType`),
  CONSTRAINT `fk_clinicalfeaturecollectiontype_1` FOREIGN KEY (`idClinicalFeature`) REFERENCES `clinicalfeature` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_clinicalfeaturecollectiontype_2` FOREIGN KEY (`idCollectionType`) REFERENCES `collectiontype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=215 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clinicalfeaturecollectiontype`
--

LOCK TABLES `clinicalfeaturecollectiontype` WRITE;
/*!40000 ALTER TABLE `clinicalfeaturecollectiontype` DISABLE KEYS */;
INSERT INTO `clinicalfeaturecollectiontype` VALUES (13,50,NULL,'Male'),(14,50,NULL,'Female'),(15,75,NULL,'NED (No evidence of disease)'),(16,75,NULL,'AWED (Alive with evidence of disease)'),(17,58,NULL,'Positive'),(18,58,NULL,'Negative'),(19,59,NULL,'Positive'),(20,59,NULL,'Negative'),(21,60,NULL,'Positive'),(22,60,NULL,'Negative'),(23,61,NULL,'Positive'),(24,61,NULL,'Negative'),(25,62,NULL,'Positive'),(26,62,NULL,'Negative'),(27,81,2,'PR_R'),(28,82,2,'ER_R'),(29,83,2,'HER_R'),(30,84,2,'Other_R'),(31,85,23,'EMA_EMC_F0'),(32,86,23,'Prekeratin_EMC_F0'),(33,87,23,'CD10_EMC_F0'),(34,88,23,'TP53_EMC_F0'),(35,89,23,'ER_EMC_F0'),(36,90,23,'PR_EMC_F0'),(37,91,23,'Phosph-S6_EMC'),(38,92,23,'p53_EMC'),(39,93,23,'MSH6_EMC'),(40,94,23,'MLH1_EMC'),(41,95,23,'MSH2_EMC'),(42,96,23,'Desmin_US_F0'),(43,97,23,'ER_US_F0'),(44,98,23,'PR_US_F0'),(45,99,23,'Caldesmon_US_F0'),(46,100,23,'AlphaSMA_US_F0'),(47,101,23,'CD10_US_F0'),(48,102,23,'Vimentin_US_F0'),(49,103,23,'Cytokeratin_US_F0'),(50,104,23,'EMA_US_F0'),(51,105,23,'PDGFR-alpha US'),(52,106,23,'Phospho-S6 US'),(53,107,23,'PTEN US'),(54,108,23,'ERBB2 US'),(55,109,23,'VEGF US'),(56,110,23,'EGFR US'),(57,111,5,'Cytokeratin_OVC_F0'),(58,112,5,'Vimentin_OVC_F0'),(59,113,5,'Phosph-S6_OVC'),(60,114,5,'TP53_OVC_F0'),(61,115,5,'MSH6_OVC'),(62,116,5,'MLH1_OVC'),(63,117,5,'MSH2_OVC'),(64,118,7,'p53 positive'),(65,126,3,'Breslow'),(66,127,3,'Mitotic Index'),(67,128,3,'Ulceration'),(68,129,3,'Clarck'),(69,130,3,'Micro Macroscopic'),(70,131,3,'Number of Lnn'),(71,132,3,'Extracapsular Dissemination'),(72,133,3,'Satellites'),(73,134,3,'In Transit Metastasis'),(74,135,3,'Skin_Non Regional lnn'),(75,136,3,'Met_lungs'),(76,137,3,'Met_Others'),(77,138,3,'Distant Metastasis'),(78,139,3,'Met_Remarks'),(79,121,2,'Triple Negative'),(80,121,2,'Adenoid cystic carcinoma'),(81,121,2,'Invasive ductal adenocarcinoma (IDA) - Not otherwise specified'),(82,121,2,'Mixed metaplastic - IDA (NOS)'),(83,121,2,'Invasive micropapillary carcinoma'),(84,121,2,'IDA with associated ductal carcinoma in situ (DCIS)'),(85,121,23,'Endometrioid - With squamous differentiation'),(86,121,23,'Mucinous'),(87,121,23,'Serous'),(88,121,23,'LMS (leiomyosarcoma)'),(89,121,23,'ESS (endometrial stromal sarcoma)'),(90,121,23,'UES (undifferentiated endometrial sarcoma)'),(91,121,23,'AS (adenosarcoma)'),(92,121,23,'CS (carcinosarcoma)'),(93,121,23,'STUMP (smooth muscle tumor of unknown malignant potential)'),(94,121,23,'NOS (not otherwise specified)'),(95,121,23,'Other'),(96,121,23,'Endometrioid - Villoglandular'),(97,121,23,'Endometrioid - Secretory'),(98,121,23,'Endometrioid -  Ciliated cell'),(99,121,23,'Endometrioid - Not specified'),(100,121,23,'Clear cell'),(101,121,23,'Mixed carcinoma'),(102,121,23,'Squamous carcinoma'),(103,121,23,'Transitional cell carcinoma'),(104,121,23,'Small cell carcinoma'),(105,121,23,'Undifferentiated carcinoma'),(106,121,23,'Unknown'),(107,121,23,'Mesonephric adenocarcinoma'),(108,121,23,'Malignant mixed mesonephric adenocarcinoma'),(109,121,23,'Trophoblastic tumor'),(110,121,23,'Undifferentiated vaginal sarcoma'),(111,121,23,'Mixed endometrioid/clear cell carcinoma'),(112,121,12,'Squamous cell carcinoma - Lip, oral cavity'),(113,121,12,'Squamous cell carcinoma - Pharynx'),(114,121,12,'Squamous cell carcinoma - Larynx'),(115,121,12,'Squamous cell carcinoma - Nasal cavity & paranasal sinus'),(116,121,12,'Squamous cell carcinoma - Major salivary glands'),(117,121,12,'Squamous cell carcinoma - Thyroid gland'),(118,121,9,'Hodgkin lymphoma'),(119,121,9,'Non-Hodgkin - Diffuse large B cell  lymphoma (DLBCL) - GCC'),(120,121,9,'Non-Hodgkin - Diffuse large B cell  lymphoma (DLBCL) - ABC'),(121,121,9,'Non-Hodgkin - Diffuse large B cell  lymphoma (DLBCL) - PMBCL'),(122,121,9,'Follicular lymphoma'),(123,121,9,'Burkitt lymphoma'),(124,121,9,'Peripheral T-Cell Lymphoma (PTCL)'),(125,121,9,'Anaplastic Large B-Cell Lymphoma ALK+ (ALCL)'),(126,121,9,'Anaplastic Large B-Cell Lymphoma ALK- (ALCL)'),(127,121,3,'Mucosal'),(128,121,3,'Uveal'),(129,121,3,'Cutaneous'),(130,121,5,'Serous adenocarcinoma'),(131,121,5,'Mucinous adenocarcinoma'),(132,121,5,'Endometrioid adenocarcinoma'),(133,121,5,'Clear cell adenocarcinoma'),(134,121,5,'Transitional cell carcinoma'),(135,121,5,'Mixed epithelial malignant tumor'),(136,121,5,'Undifferentiated carcinoma'),(137,121,5,'Sertoli-Leydig cell tumor'),(138,121,5,'Embryonal carcinoma'),(139,121,5,'Dysgerminoma'),(140,121,5,'Mullerian (endocervical-like) type of mucinous ovarian carcinoma'),(141,121,5,'Neuroectodermal ovarian tumor'),(142,121,7,'Pancreatic ductal adenocarcinoma (PDAC)'),(143,121,7,'Pancreatic neuroendocrine tumor (PNET)'),(144,121,14,'Prostate cancer'),(145,122,23,'1'),(146,122,5,'1'),(147,122,2,'1'),(148,122,23,'2'),(149,122,5,'2'),(150,122,2,'2'),(151,122,23,'3'),(152,122,5,'3'),(153,122,2,'3'),(154,122,23,'Low'),(155,122,5,'Low'),(156,122,2,'Low'),(157,122,7,'Low'),(158,122,14,'Low'),(159,122,12,'Low'),(160,122,23,'Moderate'),(161,122,5,'Moderate'),(162,122,2,'Moderate'),(163,122,7,'Moderate'),(164,122,14,'Moderate'),(165,122,12,'Moderate'),(166,122,23,'High'),(167,122,5,'High'),(168,122,2,'High'),(169,122,7,'High'),(170,122,14,'High'),(171,122,12,'High'),(172,122,23,'Unknown'),(173,122,5,'Unknown'),(174,122,2,'Unknown'),(175,122,7,'Unknown'),(176,122,14,'Unknown'),(177,122,12,'Unknown'),(178,122,23,'Blanco'),(179,122,5,'Blanco'),(180,122,2,'Blanco'),(181,122,7,'Blanco'),(182,122,14,'Blanco'),(183,122,12,'Blanco'),(184,123,23,'FIGO I'),(185,123,5,'FIGO I'),(186,123,23,'FIGO II'),(187,123,5,'FIGO II'),(188,123,23,'FIGO III'),(189,123,5,'FIGO III'),(190,123,23,'FIGO IV'),(191,123,5,'FIGO IV'),(192,124,2,'Breast'),(193,124,2,'Axillary lymph node'),(194,124,23,'Uterus'),(195,124,23,'Vagina'),(196,124,23,'Pelvis'),(197,124,23,'Peritoneum'),(198,124,23,'Cervix'),(199,124,23,'Abdomen'),(200,124,23,'Bladder'),(201,124,23,'Omentum'),(202,124,3,'Axillary Lymph node'),(203,124,3,'Inguinal Lymph node'),(204,124,5,'Abdomen'),(205,124,5,'Pelvis'),(206,124,5,'Peritoneum'),(207,124,5,'Vagina'),(208,124,5,'Ovary'),(209,124,5,'Inguinal lymph node'),(210,124,5,'Iliac lymph node'),(211,124,14,'Prostate'),(212,75,NULL,'DID (Dead of intercurrent disease)'),(213,75,NULL,'DOD (Dead of disease)'),(214,75,NULL,'Unknown');
/*!40000 ALTER TABLE `clinicalfeaturecollectiontype` ENABLE KEYS */;
UNLOCK TABLES;

delimiter //

drop trigger if exists clinfeature;
create trigger clinfeature
after update on clinicalfeaturecollectiontype
for each row
begin
if new.value <> old.value then
update collectionclinicalfeature set value=new.value where value=old.value and idClinicalFeature=new.idClinicalFeature;
end if;
end; //

delimiter ;

--
-- Table structure for table `collection`
--

DROP TABLE IF EXISTS `collection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collection` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `itemCode` varchar(10) NOT NULL,
  `idCollectionType` int(11) NOT NULL,
  `idSource` int(11) NOT NULL,
  `collectionEvent` varchar(45) NOT NULL,
  `idCollectionProtocol` int(11) DEFAULT NULL,
  `patientCode` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_Collection_TumorType1` (`idCollectionType`),
  KEY `fk_Collection_Source1` (`idSource`),
  KEY `fk_Collection_CollectionProtocol1` (`idCollectionProtocol`),
  CONSTRAINT `fk_Collection_CollectionProtocol1` FOREIGN KEY (`idCollectionProtocol`) REFERENCES `collectionprotocol` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_Collection_Source1` FOREIGN KEY (`idSource`) REFERENCES `source` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_Collection_TumorType1` FOREIGN KEY (`idCollectionType`) REFERENCES `collectiontype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1105 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `collection`
--

LOCK TABLES `collection` WRITE;
/*!40000 ALTER TABLE `collection` DISABLE KEYS */;
/*!40000 ALTER TABLE `collection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `collectionclinicalfeature`
--

DROP TABLE IF EXISTS `collectionclinicalfeature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collectionclinicalfeature` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idCollection` int(11) DEFAULT NULL,
  `idSamplingEvent` int(11) DEFAULT NULL,
  `idClinicalFeature` int(11) NOT NULL,
  `value` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_collectionclinicalfeature_1` (`idCollection`),
  KEY `fk_collectionclinicalfeature_2` (`idClinicalFeature`),
  KEY `fk_collectionclinicalfeature_3` (`idSamplingEvent`),
  CONSTRAINT `fk_collectionclinicalfeature_1` FOREIGN KEY (`idCollection`) REFERENCES `collection` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_collectionclinicalfeature_2` FOREIGN KEY (`idClinicalFeature`) REFERENCES `clinicalfeature` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_collectionclinicalfeature_3` FOREIGN KEY (`idSamplingEvent`) REFERENCES `samplingevent` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `collectionclinicalfeature`
--

LOCK TABLES `collectionclinicalfeature` WRITE;
/*!40000 ALTER TABLE `collectionclinicalfeature` DISABLE KEYS */;
/*!40000 ALTER TABLE `collectionclinicalfeature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `collectionprotocol`
--

DROP TABLE IF EXISTS `collectionprotocol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collectionprotocol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `title` varchar(100) NOT NULL,
  `project` varchar(50) NOT NULL,
  `projectDateRelease` date NOT NULL,
  `informedConsent` varchar(50) NOT NULL,
  `informedConsentDateRelease` date NOT NULL,
  `ethicalCommittee` varchar(45) NOT NULL,
  `approvalDocument` varchar(45) NOT NULL,
  `approvalDate` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `collectionprotocol`
--

LOCK TABLES `collectionprotocol` WRITE;
/*!40000 ALTER TABLE `collectionprotocol` DISABLE KEYS */;
INSERT INTO `collectionprotocol` VALUES (1,'Protocol1','Protocol1','x','2011-11-17','x','2011-06-29','x','4/2011','2011-03-09'),(2,'Protocol2','x','x','2012-05-03','x','2012-05-03','x','x','2012-05-03');
/*!40000 ALTER TABLE `collectionprotocol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `collectionprotocolinvestigator`
--

DROP TABLE IF EXISTS `collectionprotocolinvestigator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collectionprotocolinvestigator` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idCollectionProtocol` int(11) NOT NULL,
  `idPrincipalInvestigator` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_CollectionProtocolInvestigator_CollectionProtocol1` (`idCollectionProtocol`),
  KEY `fk_CollectionProtocolInvestigator_PrincipalInvestigator1` (`idPrincipalInvestigator`),
  CONSTRAINT `fk_CollectionProtocolInvestigator_CollectionProtocol1` FOREIGN KEY (`idCollectionProtocol`) REFERENCES `collectionprotocol` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_CollectionProtocolInvestigator_PrincipalInvestigator1` FOREIGN KEY (`idPrincipalInvestigator`) REFERENCES `principalinvestigator` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `collectionprotocolinvestigator`
--

LOCK TABLES `collectionprotocolinvestigator` WRITE;
/*!40000 ALTER TABLE `collectionprotocolinvestigator` DISABLE KEYS */;
/*!40000 ALTER TABLE `collectionprotocolinvestigator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `collectionprotocolparticipant`
--

DROP TABLE IF EXISTS `collectionprotocolparticipant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collectionprotocolparticipant` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idCollectionProtocol` int(11) NOT NULL,
  `idParticipant` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_CollectionProtocolParticipant_ParticipantSponsor1` (`idParticipant`),
  KEY `fk_CollectionProtocolParticipant_CollectionProtocol` (`idCollectionProtocol`),
  CONSTRAINT `fk_CollectionProtocolParticipant_CollectionProtocol` FOREIGN KEY (`idCollectionProtocol`) REFERENCES `collectionprotocol` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_CollectionProtocolParticipant_ParticipantSponsor1` FOREIGN KEY (`idParticipant`) REFERENCES `participantsponsor` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `collectionprotocolparticipant`
--

LOCK TABLES `collectionprotocolparticipant` WRITE;
/*!40000 ALTER TABLE `collectionprotocolparticipant` DISABLE KEYS */;
/*!40000 ALTER TABLE `collectionprotocolparticipant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `collectionprotocolsponsor`
--

DROP TABLE IF EXISTS `collectionprotocolsponsor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collectionprotocolsponsor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idCollectionProtocol` int(11) NOT NULL,
  `idSponsor` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_CollectionProtocolSponsor_CollectionProtocol1` (`idCollectionProtocol`),
  KEY `fk_CollectionProtocolSponsor_ParticipantSponsor1` (`idSponsor`),
  CONSTRAINT `fk_CollectionProtocolSponsor_CollectionProtocol1` FOREIGN KEY (`idCollectionProtocol`) REFERENCES `collectionprotocol` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_CollectionProtocolSponsor_ParticipantSponsor1` FOREIGN KEY (`idSponsor`) REFERENCES `participantsponsor` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `collectionprotocolsponsor`
--

LOCK TABLES `collectionprotocolsponsor` WRITE;
/*!40000 ALTER TABLE `collectionprotocolsponsor` DISABLE KEYS */;
/*!40000 ALTER TABLE `collectionprotocolsponsor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `collectiontype`
--

DROP TABLE IF EXISTS `collectiontype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collectiontype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `abbreviation` varchar(3) NOT NULL,
  `longName` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `collectiontype`
--

LOCK TABLES `collectiontype` WRITE;
/*!40000 ALTER TABLE `collectiontype` DISABLE KEYS */;
INSERT INTO `collectiontype` VALUES (1,'CRC','Colorectal'),(2,'BRC','Breast'),(3,'MEL','Melanoma'),(4,'LNG','Lung'),(5,'OVR','Ovarian'),(6,'GTR','Gastric'),(7,'EPC','Exocrin Pancreatic'),(8,'KDC','Kidney'),(9,'LNF','Lymphoma'),(10,'THC','Thyroid Cancer'),(11,'CHC','CholangioCarcinoma'),(12,'NEC','NeuroEndocrin Cancer'),(13,'HNC','Head&Neck Carcinoma'),(14,'HCC','HepatoCellularCarcinoma'),(15,'CUP','Cancer of unknown primary'),(16,'PRC','Prostate Cancer'),(17,'BLC','Bladder Cancer'),(18,'NCT','Non-Cancerous Tissue'),(19,'GIS','Gastrointestinal stromal'),(20,'TMC','Thymus Carcinoma'),(21,'ESC','Esophageal'),(22,'GBC','GallBladder Cancer'),(23,'EMC','Endometrial');
/*!40000 ALTER TABLE `collectiontype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courier`
--

DROP TABLE IF EXISTS `courier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `courier` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courier`
--

LOCK TABLES `courier` WRITE;
/*!40000 ALTER TABLE `courier` DISABLE KEYS */;
/*!40000 ALTER TABLE `courier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `derivationevent`
--

DROP TABLE IF EXISTS `derivationevent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `derivationevent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idSamplingEvent` int(11) DEFAULT NULL,
  `idAliqDerivationSchedule` int(11) DEFAULT NULL,
  `derivationDate` date NOT NULL,
  `operator` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_DerivationEvent_SamplingEvent1` (`idSamplingEvent`),
  KEY `fk_DerivationEvent_AliqDerSched1` (`idAliqDerivationSchedule`),
  CONSTRAINT `fk_DerivationEvent_AliqDerSched1` FOREIGN KEY (`idAliqDerivationSchedule`) REFERENCES `aliquotderivationschedule` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_DerivationEvent_SamplingEvent1` FOREIGN KEY (`idSamplingEvent`) REFERENCES `samplingevent` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=8661 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `derivationevent`
--

LOCK TABLES `derivationevent` WRITE;
/*!40000 ALTER TABLE `derivationevent` DISABLE KEYS */;
/*!40000 ALTER TABLE `derivationevent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `derivationprotocol`
--

DROP TABLE IF EXISTS `derivationprotocol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `derivationprotocol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idKitType` int(11) DEFAULT NULL,
  `name` varchar(45) NOT NULL,
  `loadQuantity` double DEFAULT NULL,
  `loadVolume` double DEFAULT NULL,
  `maxVolume` double DEFAULT NULL,
  `expectedVolume` double DEFAULT NULL,
  `rules` text,
  PRIMARY KEY (`id`),
  KEY `fk_Protocols_Kit1` (`idKitType`),
  CONSTRAINT `fk_Protocols_Kit1` FOREIGN KEY (`idKitType`) REFERENCES `kittype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `derivationprotocol`
--

LOCK TABLES `derivationprotocol` WRITE;
/*!40000 ALTER TABLE `derivationprotocol` DISABLE KEYS */;
INSERT INTO `derivationprotocol` VALUES (1,1,'DNA extraction1',50,NULL,NULL,100,'{\"volume_Aliquot\": \"10.0\", \"number_Aliquot\": \"5\", \"concentration_Aliquot\": \"100.0\"}'),(2,3,'DNA extraction2',20,NULL,NULL,100,'{\"volume_Aliquot\": \"10.0\", \"number_Aliquot\": \"5\", \"concentration_Aliquot\": \"100.0\"}'),(3,2,'RNA extraction1',20,NULL,NULL,30,'{\"volume_Aliquot\": \"10.0\", \"number_Aliquot\": \"5\", \"concentration_Aliquot\": \"500.0\"}'),(4,4,'cRNA',0.5,2,11,100,'{\"volume_Aliquot\": \"15\", \"number_Aliquot\": \"2\", \"concentration_Aliquot\": \"150\"}'),(5,5,'cDNA',1,2,16,20,'{\"volume_Aliquot\": \"20\", \"number_Aliquot\": \"1\", \"concentration_Aliquot\": \"3000\"}'),(6,6,'RNA extraction2',20,NULL,NULL,30,'{\"volume_Aliquot\": \"10\", \"number_Aliquot\": \"5\", \"concentration_Aliquot\": \"500\"}'),(7,7,'CirculatingDNA extraction',1,NULL,NULL,140,'{\"volume_Aliquot\": \"140\", \"number_Aliquot\": \"1\", \"concentration_Aliquot\": \"10000\"}'),(8,8,'DNA extraction3',25,NULL,NULL,100,'{\"volume_Aliquot\": \"10.0\", \"number_Aliquot\": \"5\", \"concentration_Aliquot\": \"100.0\"}'),(15,NULL,'Protein extraction1',NULL,NULL,NULL,NULL,NULL),(16,NULL,'Protein extraction2',NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `derivationprotocol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `derivationschedule`
--

DROP TABLE IF EXISTS `derivationschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `derivationschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scheduleDate` date NOT NULL,
  `operator` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=674 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `derivationschedule`
--

LOCK TABLES `derivationschedule` WRITE;
/*!40000 ALTER TABLE `derivationschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `derivationschedule` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=3419 DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'permission','auth','permission'),(2,'group','auth','group'),(3,'user','auth','user'),(4,'log entry','admin','logentry'),(5,'content type','contenttypes','contenttype'),(6,'session','sessions','session'),(7,'site','sites','site'),(8,'nonce','piston','nonce'),(9,'token','piston','token'),(10,'resource','piston','resource'),(11,'consumer','piston','consumer'),(12,'aliquot','tissue','aliquot'),(13,'aliquot derivation schedule','tissue','aliquotderivationschedule'),(14,'kit type','tissue','kittype'),(15,'kit','tissue','kit'),(16,'derivation protocol','tissue','derivationprotocol'),(17,'transformation change','tissue','transformationchange'),(18,'derivation event','tissue','derivationevent'),(19,'quality event','tissue','qualityevent'),(20,'tissue type','tissue','tissuetype'),(21,'source','tissue','source'),(22,'serie','tissue','serie'),(23,'sampling event','tissue','samplingevent'),(24,'quality schedule','tissue','qualityschedule'),(25,'aliquot quality schedule','tissue','aliquotqualityschedule'),(26,'collection type','tissue','collectiontype'),(27,'collection','tissue','collection'),(28,'transformation derivation','tissue','transformationderivation'),(29,'aliquot type','tissue','aliquottype'),(30,'urls','tissue','urls'),(31,'feature','tissue','feature'),(32,'aliquot feature','tissue','aliquotfeature'),(33,'quality event file','tissue','qualityeventfile'),(34,'position schedule','tissue','positionschedule'),(35,'aliquot position schedule','tissue','aliquotpositionschedule'),(36,'split schedule','tissue','splitschedule'),(37,'aliquot split schedule','tissue','aliquotsplitschedule'),(38,'quality protocol','tissue','qualityprotocol'),(39,'measure parameter','tissue','measureparameter'),(40,'parameter','tissue','parameter'),(41,'measure','tissue','measure'),(42,'measurement event','tissue','measurementevent'),(43,'collection protocol','tissue','collectionprotocol'),(44,'derivation schedule','tissue','derivationschedule'),(45,'aliquot experiment','tissue','aliquotexperiment'),(46,'experiment','tissue','experiment'),(47,'aliquot type experiment','tissue','aliquottypeexperiment'),(48,'instrument','tissue','instrument'),(49,'feature der protocol','tissue','featurederprotocol'),(50,'web service','tissue','webservice'),(51,'experiment schedule','tissue','experimentschedule'),(52,'mask field','tissue','maskfield'),(53,'member','tissue','member'),(54,'mask operator','tissue','maskoperator'),(55,'mask mask field','tissue','maskmaskfield'),(56,'courier','tissue','courier'),(57,'slide schedule','tissue','slideschedule');
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
-- Table structure for table `drug`
--

DROP TABLE IF EXISTS `drug`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `drug` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `externalId` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drug`
--

LOCK TABLES `drug` WRITE;
/*!40000 ALTER TABLE `drug` DISABLE KEYS */;
INSERT INTO `drug` VALUES (1,'Cetuximab',NULL),(2,'Bevacizumab',NULL),(3,'Panitumumab',NULL),(4,'Irinotecan',NULL),(5,'Trastuzumab',NULL),(6,'Lapatinib',NULL);
/*!40000 ALTER TABLE `drug` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `experiment`
--

DROP TABLE IF EXISTS `experiment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `experiment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `experiment`
--

LOCK TABLES `experiment` WRITE;
/*!40000 ALTER TABLE `experiment` DISABLE KEYS */;
INSERT INTO `experiment` VALUES (1,'MicroArray'),(2,'SangerSequencing'),(3,'RealTimePCR'),(4,'Histology-IHC'),(5,'Collaboration'),(6,'WesternBlots'),(8,'CellLineGeneration'),(10,'Sequenom'),(11,'CellLineThawing');
/*!40000 ALTER TABLE `experiment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `experimentschedule`
--

DROP TABLE IF EXISTS `experimentschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `experimentschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scheduleDate` date NOT NULL,
  `operator` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_experimentschedule_1` (`operator`),
  CONSTRAINT `fk_experimentschedule_1` FOREIGN KEY (`operator`) REFERENCES `auth_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=330 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `experimentschedule`
--

LOCK TABLES `experimentschedule` WRITE;
/*!40000 ALTER TABLE `experimentschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `experimentschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feature`
--

DROP TABLE IF EXISTS `feature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `feature` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idAliquotType` int(11) NOT NULL,
  `name` varchar(30) NOT NULL,
  `measureUnit` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_Feature_AliquotType1` (`idAliquotType`),
  CONSTRAINT `fk_Feature_AliquotType1` FOREIGN KEY (`idAliquotType`) REFERENCES `aliquottype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feature`
--

LOCK TABLES `feature` WRITE;
/*!40000 ALTER TABLE `feature` DISABLE KEYS */;
INSERT INTO `feature` VALUES (1,1,'NumberOfPieces',''),(2,2,'NumberOfPieces',''),(3,3,'NumberOfPieces',''),(4,4,'NumberOfPieces',''),(5,5,'NumberOfPieces',''),(6,6,'NumberOfPieces',''),(7,7,'Concentration','ng/ul'),(8,7,'Volume','ul'),(9,7,'OriginalConcentration','ng/ul'),(10,7,'OriginalVolume','ul'),(11,8,'Concentration','ng/ul'),(12,8,'Volume','ul'),(13,8,'OriginalConcentration','ng/ul'),(14,8,'OriginalVolume','ul'),(15,9,'Concentration','ng/ul'),(16,9,'Volume','ul'),(17,9,'OriginalConcentration','ng/ul'),(18,9,'OriginalVolume','ul'),(19,10,'Concentration','ng/ul'),(20,10,'Volume','ul'),(21,10,'OriginalConcentration','ng/ul'),(22,10,'OriginalVolume','ul'),(23,1,'Volume','ul'),(24,2,'Volume','ul'),(25,11,'Volume','ul'),(26,12,'Volume','ul'),(27,1,'Count','cell/ml'),(28,13,'Volume','ul'),(29,14,'Volume','ul'),(30,15,'Thickness','um'),(31,16,'Thickness','um'),(32,17,'Concentration','ug/ul'),(33,17,'OriginalConcentration','ug/ul'),(34,17,'Volume','ul'),(35,17,'OriginalVolume','ul');
/*!40000 ALTER TABLE `feature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `featurederaliqtype`
--

DROP TABLE IF EXISTS `featurederaliqtype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `featurederaliqtype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idFeatureDerivation` int(11) NOT NULL,
  `idAliqType` int(11) NOT NULL,
  `unityMeasure` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_idFeatDer_FeatureDerivation` (`idFeatureDerivation`),
  KEY `fk_idAliqType_AliquotType` (`idAliqType`),
  CONSTRAINT `fk_idAliqType_AliquotType` FOREIGN KEY (`idAliqType`) REFERENCES `aliquottype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_idFeatDer_FeatureDerivation` FOREIGN KEY (`idFeatureDerivation`) REFERENCES `featurederivation` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `featurederaliqtype`
--

LOCK TABLES `featurederaliqtype` WRITE;
/*!40000 ALTER TABLE `featurederaliqtype` DISABLE KEYS */;
/*!40000 ALTER TABLE `featurederaliqtype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `featurederivation`
--

DROP TABLE IF EXISTS `featurederivation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `featurederivation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `featurederivation`
--

LOCK TABLES `featurederivation` WRITE;
/*!40000 ALTER TABLE `featurederivation` DISABLE KEYS */;
INSERT INTO `featurederivation` VALUES (1,'LoadQuantity'),(2,'LoadVolume'),(3,'MaxVolume'),(4,'ExpectedVolume'),(5,'volume_Aliquot'),(6,'number_Aliquot'),(7,'concentration_Aliquot'),(8,'Instrument'),(9,'SlideType'),(10,'Thickness'),(11,'Geometry');
/*!40000 ALTER TABLE `featurederivation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `featurederprotocol`
--

DROP TABLE IF EXISTS `featurederprotocol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `featurederprotocol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idDerProtocol` int(11) NOT NULL,
  `idFeatureDerivation` int(11) NOT NULL,
  `value` double NOT NULL,
  `unityMeasure` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_idDerProtocol_idDerivationProtocol` (`idDerProtocol`),
  KEY `fk_idFeatureDerivation_featDer` (`idFeatureDerivation`),
  CONSTRAINT `fk_idDerProtocol_idDerivationProtocol` FOREIGN KEY (`idDerProtocol`) REFERENCES `derivationprotocol` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_idFeatureDerivation_featDer` FOREIGN KEY (`idFeatureDerivation`) REFERENCES `featurederivation` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `featurederprotocol`
--

LOCK TABLES `featurederprotocol` WRITE;
/*!40000 ALTER TABLE `featurederprotocol` DISABLE KEYS */;
INSERT INTO `featurederprotocol` VALUES (1,3,1,20,'mg'),(2,3,4,30,'ul'),(3,3,5,10,'ul'),(4,3,6,5,''),(5,3,7,500,'ng/ul'),(6,1,1,50,'mg'),(7,1,4,100,'ul'),(8,1,5,10,'ul'),(9,1,6,5,''),(10,1,7,100,'ng/ul'),(11,4,1,0.5,'ug'),(12,4,2,2,'ul'),(13,4,3,11,'ul'),(14,4,4,100,'ul'),(15,4,5,15,'ul'),(16,4,6,2,''),(17,4,7,150,'ng/ul'),(18,5,1,1,'ug'),(19,5,2,2,'ul'),(20,5,3,16,'ul'),(21,5,4,20,'ul'),(22,5,5,20,'ul'),(23,5,6,1,''),(24,5,7,3000,'ng/ul'),(25,2,1,20,'mg'),(26,2,4,100,'ul'),(27,2,5,10,'ul'),(28,2,6,5,''),(29,2,7,100,'ng/ul'),(30,6,1,20,'mg'),(31,6,4,30,'ul'),(32,6,5,10,'ul'),(33,6,6,5,''),(34,6,7,500,'ng/ul'),(35,7,2,1000,'ul'),(36,7,4,140,'ul'),(37,7,5,140,'ul'),(38,7,6,1,''),(39,7,7,10000,'ng/ul'),(40,8,1,25,'mg'),(41,8,4,100,'ul'),(42,8,5,10,'ul'),(43,8,6,5,''),(44,8,7,100,'ng/ul'),(45,15,1,0,'mg'),(46,15,4,0,''),(47,15,5,20,'ul'),(48,15,6,1,''),(49,15,7,3000,'ng/ul'),(50,16,1,0,'mg'),(51,16,4,0,''),(52,16,5,20,'ul'),(53,16,6,1,''),(54,16,7,3000,'ng/ul');
/*!40000 ALTER TABLE `featurederprotocol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `featureslideprotocol`
--

DROP TABLE IF EXISTS `featureslideprotocol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `featureslideprotocol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idSlideProtocol` int(11) NOT NULL,
  `idFeatureDerivation` int(11) NOT NULL,
  `value` varchar(30) NOT NULL,
  `unityMeasure` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_featureslideprotocol_1` (`idSlideProtocol`),
  KEY `fk_featureslideprotocol_2` (`idFeatureDerivation`),
  CONSTRAINT `fk_featureslideprotocol_1` FOREIGN KEY (`idSlideProtocol`) REFERENCES `slideprotocol` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_featureslideprotocol_2` FOREIGN KEY (`idFeatureDerivation`) REFERENCES `featurederivation` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `featureslideprotocol`
--

LOCK TABLES `featureslideprotocol` WRITE;
/*!40000 ALTER TABLE `featureslideprotocol` DISABLE KEYS */;
INSERT INTO `featureslideprotocol` VALUES (1,1,8,'Cryostat',NULL),(2,1,9,'SlideCryostat',NULL),(3,1,10,'10','um'),(4,1,11,'1x3',NULL),(5,2,8,'Microtome',NULL),(6,2,9,'SlideMicrotome',NULL),(7,2,10,'5','um'),(8,2,11,'1x2',NULL);
/*!40000 ALTER TABLE `featureslideprotocol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `instrument`
--

DROP TABLE IF EXISTS `instrument`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `instrument` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(45) NOT NULL,
  `name` varchar(45) NOT NULL,
  `manufacturer` varchar(45) DEFAULT NULL,
  `description` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `instrument`
--

LOCK TABLES `instrument` WRITE;
/*!40000 ALTER TABLE `instrument` DISABLE KEYS */;
INSERT INTO `instrument` VALUES (1,'8000','NANODROP','Thermo Scientific',''),(2,'2100','BIOANALYZER','Agilent',''),(3,'5656','Instrument1','z','Beaming'),(4,'Q32866','QUBIT','Life Technologies','Beaming'),(5,'DU640','Specrophotometer1','Beckman','IRCC code - 03282'),(6,'XY4522','SPECTROPHOTOMETER2','x','');
/*!40000 ALTER TABLE `instrument` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kit`
--

DROP TABLE IF EXISTS `kit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `kit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idKitType` int(11) NOT NULL,
  `barcode` varchar(45) NOT NULL,
  `openDate` date DEFAULT NULL,
  `expirationDate` date NOT NULL,
  `remainingCapacity` int(11) NOT NULL,
  `lotNumber` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_KitBatch_Kits1` (`idKitType`),
  CONSTRAINT `fk_KitBatch_Kits1` FOREIGN KEY (`idKitType`) REFERENCES `kittype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=106 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kit`
--

LOCK TABLES `kit` WRITE;
/*!40000 ALTER TABLE `kit` DISABLE KEYS */;
/*!40000 ALTER TABLE `kit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kit_audit`
--

DROP TABLE IF EXISTS `kit_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `kit_audit` (
  `id` int(11) NOT NULL,
  `idKitType` int(11) NOT NULL,
  `barcode` varchar(45) NOT NULL,
  `openDate` date DEFAULT NULL,
  `expirationDate` date NOT NULL,
  `remainingCapacity` int(11) NOT NULL,
  `lotNumber` varchar(45) DEFAULT NULL,
  `username` varchar(30) NOT NULL,
  `_audit_id` int(11) NOT NULL AUTO_INCREMENT,
  `_audit_timestamp` datetime NOT NULL,
  `_audit_change_type` varchar(1) NOT NULL,
  PRIMARY KEY (`_audit_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4637 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kit_audit`
--

LOCK TABLES `kit_audit` WRITE;
/*!40000 ALTER TABLE `kit_audit` DISABLE KEYS */;
/*!40000 ALTER TABLE `kit_audit` ENABLE KEYS */;
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
CREATE TRIGGER `audit_kit` BEFORE INSERT ON `kit_audit` FOR EACH ROW begin
if new._audit_change_type= 'I' then
select id into @id
from kit
where kit.barcode= new.barcode and kit.idKitType=new.idKitType;
set new.id=@id;
END if;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `kittype`
--

DROP TABLE IF EXISTS `kittype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `kittype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `capacity` int(11) NOT NULL,
  `producer` varchar(45) DEFAULT NULL,
  `catalogueNumber` varchar(45) DEFAULT NULL,
  `instructions` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kittype`
--

LOCK TABLES `kittype` WRITE;
/*!40000 ALTER TABLE `kittype` DISABLE KEYS */;
INSERT INTO `kittype` VALUES (1,'DNAKit1 (25)',25,'Qiagen','13343','QIAGEN_Genomic_DNA_Handbook.pdf'),(2,'RNAKit1 (50)',50,'Qiagen','217094','miRNeasy_Mini_Handbook.pdf'),(3,'DNAKit2 (50)',50,'Qiagen','69504','DNeasy_Blood_&_Tissue_Handbook.pdf'),(4,'cRNAKit',24,'Ambion','AMIL1791','Illumina_Totalprep_RNA.pdf'),(5,'cDNAKit1 (100)',100,'Biorad','1708841','iScriptBiorad.pdf'),(6,'RNAKit2',100,'Roche','03270289001',''),(7,'CirculatingDNAKit',50,'Qiagen','55114','EN-QIAamp-Circulating-Nucleic-Acid-Handbook.pdf'),(8,'DNAKit3 (100)',100,'Promega','A2051','ReliaPrep gDNA Tissue Miniprep System.pdf'),(9,'cDNAKit2',200,'Applied Biosystems','4368814','');
/*!40000 ALTER TABLE `kittype` ENABLE KEYS */;
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
-- Table structure for table `mask`
--

DROP TABLE IF EXISTS `mask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mask` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mask`
--

LOCK TABLES `mask` WRITE;
/*!40000 ALTER TABLE `mask` DISABLE KEYS */;
INSERT INTO `mask` VALUES (1,'Mask1'),(2,'Mask2'),(3,'NoMask');
/*!40000 ALTER TABLE `mask` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maskfield`
--

DROP TABLE IF EXISTS `maskfield`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `maskfield` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) NOT NULL,
  `identifier` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maskfield`
--

LOCK TABLES `maskfield` WRITE;
/*!40000 ALTER TABLE `maskfield` DISABLE KEYS */;
INSERT INTO `maskfield` VALUES (1,'Collection type','-1'),(2,'Case','-1'),(3,'Tissue','-1'),(4,'Aliquot type','-1'),(5,'Aliquot ID','-1'),(6,'Further info','-1'),(7,'Coll. date','-1'),(8,'Barcode','-1'),(9,'Conc.(ng/ul)','33'),(10,'Volume(ul)','34');
/*!40000 ALTER TABLE `maskfield` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maskmaskfield`
--

DROP TABLE IF EXISTS `maskmaskfield`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `maskmaskfield` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idMask` int(11) NOT NULL,
  `idMaskField` int(11) NOT NULL,
  `encrypted` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_maskmaskfield_1` (`idMask`),
  KEY `fk_maskmaskfield_2` (`idMaskField`),
  CONSTRAINT `fk_maskmaskfield_1` FOREIGN KEY (`idMask`) REFERENCES `mask` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_maskmaskfield_2` FOREIGN KEY (`idMaskField`) REFERENCES `maskfield` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maskmaskfield`
--

LOCK TABLES `maskmaskfield` WRITE;
/*!40000 ALTER TABLE `maskmaskfield` DISABLE KEYS */;
INSERT INTO `maskmaskfield` VALUES (1,1,1,0),(2,1,2,0),(3,1,3,0),(4,1,4,0),(5,1,5,0),(6,1,6,0),(7,1,7,0),(8,1,8,0),(9,2,1,0),(10,2,2,1),(11,2,3,0),(12,2,4,0),(13,2,5,0),(14,2,6,0),(15,2,7,1),(16,2,8,0),(17,3,1,0),(18,3,2,0),(19,3,3,0),(20,3,4,0),(21,3,5,0),(22,3,6,0),(23,3,7,0),(24,3,8,0),(25,1,9,0),(26,1,10,0);
/*!40000 ALTER TABLE `maskmaskfield` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maskoperator`
--

DROP TABLE IF EXISTS `maskoperator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `maskoperator` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idMask` int(11) NOT NULL,
  `operator` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_maskoperator_1` (`idMask`),
  KEY `fk_maskoperator_2` (`operator`),
  CONSTRAINT `fk_maskoperator_1` FOREIGN KEY (`idMask`) REFERENCES `mask` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_maskoperator_2` FOREIGN KEY (`operator`) REFERENCES `auth_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maskoperator`
--

LOCK TABLES `maskoperator` WRITE;
/*!40000 ALTER TABLE `maskoperator` DISABLE KEYS */;
/*!40000 ALTER TABLE `maskoperator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `measure`
--

DROP TABLE IF EXISTS `measure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `measure` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idInstrument` int(11) NOT NULL,
  `name` varchar(30) NOT NULL,
  `measureUnit` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_Measure_Instrument1` (`idInstrument`),
  CONSTRAINT `fk_Measure_Instrument1` FOREIGN KEY (`idInstrument`) REFERENCES `instrument` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `measure`
--

LOCK TABLES `measure` WRITE;
/*!40000 ALTER TABLE `measure` DISABLE KEYS */;
INSERT INTO `measure` VALUES (1,1,'concentration','ng/ul'),(2,1,'purity','260/280'),(3,1,'purity','260/230'),(4,2,'concentration','ng/ul'),(5,2,'quality','RIN'),(6,3,'GE/Vex','GE/ml'),(7,3,'concentration','ng/ul'),(8,4,'concentration','ng/ul'),(14,5,'concentration','ug/ul'),(15,5,'absorbance','562nm');
/*!40000 ALTER TABLE `measure` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `measurementevent`
--

DROP TABLE IF EXISTS `measurementevent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `measurementevent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idMeasure` int(11) NOT NULL,
  `idQualityEvent` int(11) NOT NULL,
  `value` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_Measure_MeasureType1` (`idMeasure`),
  KEY `fk_MeasurementEvent_QualityEvent1` (`idQualityEvent`),
  CONSTRAINT `fk_MeasurementEvent_QualityEvent1` FOREIGN KEY (`idQualityEvent`) REFERENCES `qualityevent` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_Measure_MeasureType1` FOREIGN KEY (`idMeasure`) REFERENCES `measure` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=20974 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `measurementevent`
--

LOCK TABLES `measurementevent` WRITE;
/*!40000 ALTER TABLE `measurementevent` DISABLE KEYS */;
/*!40000 ALTER TABLE `measurementevent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `measureparameter`
--

DROP TABLE IF EXISTS `measureparameter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `measureparameter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idMeasure` int(11) NOT NULL,
  `idParameter` int(11) NOT NULL,
  `idQualityProtocol` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_MeasureParameter_Measure1` (`idMeasure`),
  KEY `fk_MeasureParameter_Parameter1` (`idParameter`),
  KEY `fk_MeasureParameter_QualityProtocol1` (`idQualityProtocol`),
  CONSTRAINT `fk_MeasureParameter_Measure1` FOREIGN KEY (`idMeasure`) REFERENCES `measure` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_MeasureParameter_Parameter1` FOREIGN KEY (`idParameter`) REFERENCES `parameter` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_MeasureParameter_QualityProtocol1` FOREIGN KEY (`idQualityProtocol`) REFERENCES `qualityprotocol` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `measureparameter`
--

LOCK TABLES `measureparameter` WRITE;
/*!40000 ALTER TABLE `measureparameter` DISABLE KEYS */;
INSERT INTO `measureparameter` VALUES (1,1,1,1),(2,2,1,1),(3,3,1,1),(4,1,1,2),(5,2,1,2),(6,3,1,2),(7,4,1,2),(8,5,1,2),(9,1,1,3),(10,2,1,3),(11,3,1,3),(12,1,1,4),(13,2,1,4),(14,3,1,4),(15,4,1,4),(16,1,1,5),(17,2,1,5),(18,3,1,5),(19,6,1,5),(20,7,1,5),(21,6,1,6),(22,8,1,6),(23,7,1,6),(24,14,1,8),(25,15,1,8);
/*!40000 ALTER TABLE `measureparameter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mousetissuetype`
--

DROP TABLE IF EXISTS `mousetissuetype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mousetissuetype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `abbreviation` varchar(3) NOT NULL,
  `longName` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mousetissuetype`
--

LOCK TABLES `mousetissuetype` WRITE;
/*!40000 ALTER TABLE `mousetissuetype` DISABLE KEYS */;
INSERT INTO `mousetissuetype` VALUES (1,'TUM','Tumor'),(2,'LNG','Lung'),(3,'LIV','Liver'),(4,'GUT','Gut'),(5,'BLD','Blood'),(6,'MLI','Liver Mets'),(7,'MBR','Brain Mets'),(8,'MLN','Lung Mets');
/*!40000 ALTER TABLE `mousetissuetype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parameter`
--

DROP TABLE IF EXISTS `parameter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `parameter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `measureUnit` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parameter`
--

LOCK TABLES `parameter` WRITE;
/*!40000 ALTER TABLE `parameter` DISABLE KEYS */;
INSERT INTO `parameter` VALUES (1,'wavelength','nm');
/*!40000 ALTER TABLE `parameter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `participantsponsor`
--

DROP TABLE IF EXISTS `participantsponsor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `participantsponsor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  `base` varchar(40) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `participantsponsor`
--

LOCK TABLES `participantsponsor` WRITE;
/*!40000 ALTER TABLE `participantsponsor` DISABLE KEYS */;
/*!40000 ALTER TABLE `participantsponsor` ENABLE KEYS */;
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
-- Table structure for table `positionschedule`
--

DROP TABLE IF EXISTS `positionschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `positionschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scheduleDate` date NOT NULL,
  `operator` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `positionschedule`
--

LOCK TABLES `positionschedule` WRITE;
/*!40000 ALTER TABLE `positionschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `positionschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `principalinvestigator`
--

DROP TABLE IF EXISTS `principalinvestigator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `principalinvestigator` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `surname` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `principalinvestigator`
--

LOCK TABLES `principalinvestigator` WRITE;
/*!40000 ALTER TABLE `principalinvestigator` DISABLE KEYS */;
/*!40000 ALTER TABLE `principalinvestigator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `qualityevent`
--

DROP TABLE IF EXISTS `qualityevent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `qualityevent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idQualityProtocol` int(11) NOT NULL,
  `idQualitySchedule` int(11) DEFAULT NULL COMMENT '	',
  `idAliquot` int(11) NOT NULL,
  `idAliquotDerivationSchedule` int(11) DEFAULT NULL,
  `misurationDate` date NOT NULL,
  `insertionDate` date DEFAULT NULL,
  `operator` varchar(45) NOT NULL,
  `quantityUsed` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_QualityEvent_Aliquots1` (`idAliquot`),
  KEY `fk_QualityEvent_QualityProtocol1` (`idQualityProtocol`),
  KEY `fk_QualityEvent_QualitySchedule1` (`idQualitySchedule`),
  KEY `fk_QualityEvent_AliqDerSched1` (`idAliquotDerivationSchedule`),
  CONSTRAINT `fk_QualityEvent_AliqDerSched1` FOREIGN KEY (`idAliquotDerivationSchedule`) REFERENCES `aliquotderivationschedule` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_QualityEvent_Aliquots1` FOREIGN KEY (`idAliquot`) REFERENCES `aliquot` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_QualityEvent_QualityProtocol1` FOREIGN KEY (`idQualityProtocol`) REFERENCES `qualityprotocol` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_QualityEvent_QualitySchedule1` FOREIGN KEY (`idQualitySchedule`) REFERENCES `qualityschedule` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=8954 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qualityevent`
--

LOCK TABLES `qualityevent` WRITE;
/*!40000 ALTER TABLE `qualityevent` DISABLE KEYS */;
/*!40000 ALTER TABLE `qualityevent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `qualityeventfile`
--

DROP TABLE IF EXISTS `qualityeventfile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `qualityeventfile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idQualityEvent` int(11) NOT NULL,
  `file` varchar(150) NOT NULL,
  `judge` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_QualityEventFile_QualityEvent1` (`idQualityEvent`),
  CONSTRAINT `fk_QualityEventFile_QualityEvent1` FOREIGN KEY (`idQualityEvent`) REFERENCES `qualityevent` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qualityeventfile`
--

LOCK TABLES `qualityeventfile` WRITE;
/*!40000 ALTER TABLE `qualityeventfile` DISABLE KEYS */;
/*!40000 ALTER TABLE `qualityeventfile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `qualityprotocol`
--

DROP TABLE IF EXISTS `qualityprotocol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `qualityprotocol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idAliquotType` int(11) NOT NULL,
  `name` varchar(30) NOT NULL,
  `description` varchar(150) DEFAULT NULL,
  `mandatoryFields` tinyint(4) DEFAULT NULL,
  `quantityUsed` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_QualityProtocol_AliquotType1` (`idAliquotType`),
  CONSTRAINT `fk_QualityProtocol_AliquotType1` FOREIGN KEY (`idAliquotType`) REFERENCES `aliquottype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qualityprotocol`
--

LOCK TABLES `qualityprotocol` WRITE;
/*!40000 ALTER TABLE `qualityprotocol` DISABLE KEYS */;
INSERT INTO `qualityprotocol` VALUES (1,7,'DNAMeasure','',0,1),(2,8,'RNAMeasure','',0,2),(3,9,'cDNAMeasure','',0,1),(4,10,'cRNAMeasure','',0,2),(5,7,'CirculatingDNA Nanodrop','circulating DNA',0,19.5),(6,7,'CirculatingDNA Qubit','Protocollo per beaming',0,19),(8,17,'ProteinMeasure','',1,5);
/*!40000 ALTER TABLE `qualityprotocol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `qualityschedule`
--

DROP TABLE IF EXISTS `qualityschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `qualityschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scheduleDate` date NOT NULL,
  `operator` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qualityschedule`
--

LOCK TABLES `qualityschedule` WRITE;
/*!40000 ALTER TABLE `qualityschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `qualityschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `samplingevent`
--

DROP TABLE IF EXISTS `samplingevent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `samplingevent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idTissueType` int(11) DEFAULT NULL,
  `idCollection` int(11) NOT NULL,
  `idSource` int(11) NOT NULL,
  `idSerie` int(11) NOT NULL,
  `samplingDate` date NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_Tissues_TissuesType1` (`idTissueType`),
  KEY `fk_SamplingEvent_Source1` (`idSource`),
  KEY `fk_SamplingEvent_Series1` (`idSerie`),
  KEY `fk_SamplingEvents_Collection1` (`idCollection`),
  CONSTRAINT `fk_SamplingEvents_Collection1` FOREIGN KEY (`idCollection`) REFERENCES `collection` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_SamplingEvent_Series1` FOREIGN KEY (`idSerie`) REFERENCES `serie` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_SamplingEvent_Source1` FOREIGN KEY (`idSource`) REFERENCES `source` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_Tissues_TissuesType1` FOREIGN KEY (`idTissueType`) REFERENCES `tissuetype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=19221 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `samplingevent`
--

LOCK TABLES `samplingevent` WRITE;
/*!40000 ALTER TABLE `samplingevent` DISABLE KEYS */;
/*!40000 ALTER TABLE `samplingevent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `serie`
--

DROP TABLE IF EXISTS `serie`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `serie` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `operator` varchar(30) NOT NULL,
  `serieDate` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3788 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `serie`
--

LOCK TABLES `serie` WRITE;
/*!40000 ALTER TABLE `serie` DISABLE KEYS */;
/*!40000 ALTER TABLE `serie` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `slideprotocol`
--

DROP TABLE IF EXISTS `slideprotocol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `slideprotocol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `slideprotocol`
--

LOCK TABLES `slideprotocol` WRITE;
/*!40000 ALTER TABLE `slideprotocol` DISABLE KEYS */;
INSERT INTO `slideprotocol` VALUES (1,'Cryostat'),(2,'Microtome');
/*!40000 ALTER TABLE `slideprotocol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `slideschedule`
--

DROP TABLE IF EXISTS `slideschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `slideschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scheduleDate` date NOT NULL,
  `operator` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `slideschedule`
--

LOCK TABLES `slideschedule` WRITE;
/*!40000 ALTER TABLE `slideschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `slideschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `source`
--

DROP TABLE IF EXISTS `source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `source` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `type` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `source`
--

LOCK TABLES `source` WRITE;
/*!40000 ALTER TABLE `source` DISABLE KEYS */;
INSERT INTO `source` VALUES (1,'caxeno','Las'),(2,'cellline','Las');
/*!40000 ALTER TABLE `source` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `splischedule`
--

DROP TABLE IF EXISTS `splischedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `splischedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scheduleDate` date NOT NULL,
  `operator` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `splischedule`
--

LOCK TABLES `splischedule` WRITE;
/*!40000 ALTER TABLE `splischedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `splischedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tissue_member`
--

DROP TABLE IF EXISTS `tissue_member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tissue_member` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tissue_member`
--

LOCK TABLES `tissue_member` WRITE;
/*!40000 ALTER TABLE `tissue_member` DISABLE KEYS */;
/*!40000 ALTER TABLE `tissue_member` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tissue_wg`
--

DROP TABLE IF EXISTS `tissue_wg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tissue_wg` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tissue_wg_5d52dd10` (`owner_id`),
  CONSTRAINT `owner_id_refs_id_d6eed27b` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tissue_wg`
--

LOCK TABLES `tissue_wg` WRITE;
/*!40000 ALTER TABLE `tissue_wg` DISABLE KEYS */;
/*!40000 ALTER TABLE `tissue_wg` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tissue_wg_user`
--

DROP TABLE IF EXISTS `tissue_wg_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tissue_wg_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `WG_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tissue_wg_user_e2a12238` (`WG_id`),
  KEY `tissue_wg_user_fbfc09f1` (`user_id`),
  KEY `tissue_wg_user_1e014c8f` (`permission_id`),
  CONSTRAINT `permission_id_refs_id_2fe3d2b0` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `user_id_refs_id_ad0772ce` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `WG_id_refs_id_1fcabd38` FOREIGN KEY (`WG_id`) REFERENCES `tissue_wg` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9731 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tissue_wg_user`
--

LOCK TABLES `tissue_wg_user` WRITE;
/*!40000 ALTER TABLE `tissue_wg_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `tissue_wg_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tissuetype`
--

DROP TABLE IF EXISTS `tissuetype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tissuetype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `abbreviation` varchar(2) NOT NULL,
  `longName` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tissuetype`
--

LOCK TABLES `tissuetype` WRITE;
/*!40000 ALTER TABLE `tissuetype` DISABLE KEYS */;
INSERT INTO `tissuetype` VALUES (1,'PR','Primary Tumor'),(2,'LM','Liver Met'),(3,'CM','Cutaneous Met'),(4,'PM','Peritoneal Met'),(5,'TM','Lung Met'),(6,'BM','Brain Met'),(7,'SM','Bone Met'),(8,'TR','Thoracentesis'),(9,'TH','Thymus Met'),(10,'LY','Lymphnode Met'),(11,'AM','Adrenal Met'),(12,'NL','Normal Liver'),(13,'NB','Normal Brain'),(14,'NN','Normal Lymphnode'),(15,'NM','Normal Mucosa'),(16,'NC','Normal Cutis'),(17,'BL','Blood'),(18,'MP','Prostate Met'),(19,'MB','Bladder Met'),(20,'NP','Normal Prostate'),(21,'ND','Normal Bladder'),(22,'UR','Urine'),(23,'HL','Hyperplastic Liver'),(24,'OM','Ovarian Metastasis');
/*!40000 ALTER TABLE `tissuetype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transfer`
--

DROP TABLE IF EXISTS `transfer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transfer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idTransferSchedule` int(11) NOT NULL,
  `operator` int(11) DEFAULT NULL,
  `addressTo` int(11) NOT NULL,
  `plannedDepartureDate` date DEFAULT NULL,
  `departureDate` date DEFAULT NULL,
  `departureExecuted` tinyint(1) NOT NULL,
  `deliveryDate` date DEFAULT NULL,
  `deliveryExecuted` tinyint(1) NOT NULL,
  `idCourier` int(11) DEFAULT NULL,
  `trackingNumber` varchar(45) DEFAULT NULL,
  `deleteTimestamp` datetime DEFAULT NULL,
  `deleteOperator` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_transfer_1` (`idTransferSchedule`),
  KEY `fk_transfer_2` (`operator`),
  KEY `fk_transfer_3` (`addressTo`),
  KEY `fk_transfer_4` (`idCourier`),
  KEY `fk_transfer_5` (`deleteOperator`),
  CONSTRAINT `fk_transfer_1` FOREIGN KEY (`idTransferSchedule`) REFERENCES `transferschedule` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_transfer_2` FOREIGN KEY (`operator`) REFERENCES `auth_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_transfer_3` FOREIGN KEY (`addressTo`) REFERENCES `auth_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_transfer_4` FOREIGN KEY (`idCourier`) REFERENCES `courier` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_transfer_5` FOREIGN KEY (`deleteOperator`) REFERENCES `auth_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transfer`
--

LOCK TABLES `transfer` WRITE;
/*!40000 ALTER TABLE `transfer` DISABLE KEYS */;
/*!40000 ALTER TABLE `transfer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transferschedule`
--

DROP TABLE IF EXISTS `transferschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transferschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scheduleDate` date NOT NULL,
  `operator` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_transferschedule_1` (`operator`),
  CONSTRAINT `fk_transferschedule_1` FOREIGN KEY (`operator`) REFERENCES `auth_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transferschedule`
--

LOCK TABLES `transferschedule` WRITE;
/*!40000 ALTER TABLE `transferschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `transferschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transformationchange`
--

DROP TABLE IF EXISTS `transformationchange`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transformationchange` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idFromType` int(11) NOT NULL,
  `idToType` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_TransformationChange_AliquotType1` (`idFromType`),
  KEY `fk_TransformationChange_AliquotType2` (`idToType`),
  CONSTRAINT `fk_TransformationChange_AliquotType1` FOREIGN KEY (`idFromType`) REFERENCES `aliquottype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_TransformationChange_AliquotType2` FOREIGN KEY (`idToType`) REFERENCES `aliquottype` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transformationchange`
--

LOCK TABLES `transformationchange` WRITE;
/*!40000 ALTER TABLE `transformationchange` DISABLE KEYS */;
INSERT INTO `transformationchange` VALUES (1,1,7),(2,2,7),(3,3,7),(4,4,7),(5,1,8),(6,2,8),(7,3,8),(8,4,8),(9,6,8),(10,8,9),(11,8,10),(12,11,7),(13,12,7),(16,4,15),(17,5,16),(18,1,17),(19,2,17),(20,3,17),(21,4,17);
/*!40000 ALTER TABLE `transformationchange` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transformationderivation`
--

DROP TABLE IF EXISTS `transformationderivation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transformationderivation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idDerivationProtocol` int(11) NOT NULL,
  `idTransformationChange` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_TransformationDerivation_DerivationProtocol1` (`idDerivationProtocol`),
  KEY `fk_TransformationDerivation_TransformationChange1` (`idTransformationChange`),
  CONSTRAINT `fk_TransformationDerivation_DerivationProtocol1` FOREIGN KEY (`idDerivationProtocol`) REFERENCES `derivationprotocol` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_TransformationDerivation_TransformationChange1` FOREIGN KEY (`idTransformationChange`) REFERENCES `transformationchange` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transformationderivation`
--

LOCK TABLES `transformationderivation` WRITE;
/*!40000 ALTER TABLE `transformationderivation` DISABLE KEYS */;
INSERT INTO `transformationderivation` VALUES (1,1,1),(2,1,2),(3,1,3),(4,1,4),(5,2,1),(6,2,2),(7,2,3),(8,2,4),(9,3,5),(10,3,6),(11,3,7),(12,3,9),(13,4,11),(14,5,10),(15,6,8),(16,7,1),(17,7,2),(18,7,12),(19,7,13),(20,8,1),(21,8,2),(22,8,3),(23,8,4),(34,15,18),(35,15,19),(36,15,20),(37,15,21),(38,16,18),(39,16,19),(40,16,20),(41,16,21);
/*!40000 ALTER TABLE `transformationderivation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transformationslide`
--

DROP TABLE IF EXISTS `transformationslide`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transformationslide` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idSlideProtocol` int(11) NOT NULL,
  `idTransformationChange` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_transformationslide_1` (`idSlideProtocol`),
  KEY `fk_transformationslide_2` (`idTransformationChange`),
  CONSTRAINT `fk_transformationslide_1` FOREIGN KEY (`idSlideProtocol`) REFERENCES `slideprotocol` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_transformationslide_2` FOREIGN KEY (`idTransformationChange`) REFERENCES `transformationchange` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transformationslide`
--

LOCK TABLES `transformationslide` WRITE;
/*!40000 ALTER TABLE `transformationslide` DISABLE KEYS */;
INSERT INTO `transformationslide` VALUES (1,1,17),(2,2,16);
/*!40000 ALTER TABLE `transformationslide` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `url`
--

DROP TABLE IF EXISTS `url`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `url` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(60) NOT NULL,
  `default` tinyint(1) NOT NULL,
  `idWebService` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_url_1` (`idWebService`),
  CONSTRAINT `fk_url_1` FOREIGN KEY (`idWebService`) REFERENCES `webservice` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `url`
--

LOCK TABLES `url` WRITE;
/*!40000 ALTER TABLE `url` DISABLE KEYS */;
INSERT INTO `url` VALUES (1,'http://emageda.polito.it:8000',0,NULL),(2,'http://devircc.polito.it/storage',0,NULL),(3,'/storage',1,NULL),(4,'/micro',0,2),(5,'/realTime',0,3),(6,'/sanger',0,4),(7,'/cellline',0,5),(8,'/cellline',0,6),(9,'/fingerPrinting',0,7),(10,'/annotations',0,8),(11,'/mdam',0,9),(12,'/las',0,10);
/*!40000 ALTER TABLE `url` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webservice`
--

DROP TABLE IF EXISTS `webservice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `webservice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webservice`
--

LOCK TABLES `webservice` WRITE;
/*!40000 ALTER TABLE `webservice` DISABLE KEYS */;
INSERT INTO `webservice` VALUES (1,'Beaming'),(2,'MicroArray'),(3,'RealTimePCR'),(4,'SangerSequencing'),(5,'CellLineGeneration'),(6,'CellLineThawing'),(7,'FingerPrinting'),(8,'Annotation'),(9,'MDAM'),(10,'LASAuthServer');
/*!40000 ALTER TABLE `webservice` ENABLE KEYS */;
UNLOCK TABLES;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-11-11  2:00:10
