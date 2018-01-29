CREATE TABLE `container_audit` (
  `id` int(11) NOT NULL,
  `idContainerType` integer NOT NULL,
  `idFatherContainer` int(11) DEFAULT NULL,
  `position` varchar(10) ,
  `barcode` varchar(45) NOT NULL,
  `availability` bool NOT NULL,
  `full` bool NOT NULL,
  `owner` varchar(45) DEFAULT NULL,
  `username` varchar(30) NOT NULL,
  `_audit_id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `_audit_timestamp` datetime NOT NULL,
  `_audit_change_type` varchar(1) NOT NULL
);

CREATE  TABLE `storage`.`aliquot_audit` (
  `id` INT NOT NULL ,
  `genealogyID` VARCHAR(30) NOT NULL ,
  `idContainer` INT NULL ,
  `position` VARCHAR(10) NULL ,
  `startTimestamp` datetime DEFAULT NULL,
  `endTimestamp` datetime DEFAULT NULL,
  `startOperator` int(11) DEFAULT NULL,
  `endOperator` int(11) DEFAULT NULL,
  `username` varchar(30) NOT NULL,
  `_audit_id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `_audit_timestamp` datetime NOT NULL,
  `_audit_change_type` varchar(1) NOT NULL
);
