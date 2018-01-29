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
  `_audit_id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `_audit_timestamp` datetime NOT NULL,
  `_audit_change_type` varchar(1) NOT NULL
);

CREATE TABLE `kit_audit` (
  `id` int(11) NOT NULL,
  `idKitType` int(11) NOT NULL,
  `barcode` varchar(45) NOT NULL,
  `openDate` date DEFAULT NULL,
  `expirationDate` date NOT NULL,
  `remainingCapacity` int(11) NOT NULL,
  `lotNumber` varchar(45) DEFAULT NULL,
  `username` varchar(30) NOT NULL,
  `_audit_id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `_audit_timestamp` datetime NOT NULL,
  `_audit_change_type` varchar(1) NOT NULL
 );
 
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
  `username` varchar(30) NOT NULL,
  `_audit_id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `_audit_timestamp` datetime NOT NULL,
  `_audit_change_type` varchar(1) NOT NULL
 );

