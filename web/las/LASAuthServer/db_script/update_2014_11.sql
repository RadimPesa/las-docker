CREATE  TABLE IF NOT EXISTS `lasauthserver`.`loginmanager_menucat` (
  `id` INT(11) NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(128) NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `menucat_name_UNIQUE` (`name` ASC) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;

ALTER TABLE `lasauthserver`.`loginmanager_lasmodule` ADD COLUMN `menucat_id` int(11), ADD CONSTRAINT `fk_menucat_lasmodule` FOREIGN KEY (`menucat_id`) REFERENCES `lasauthserver`.`loginmanager_menucat`(`id`);

insert into `lasauthserver`.`loginmanager_menucat` values (1, 'Manage Samples & Archives'), (2, 'Biological Experiments'), (3, 'Molecular Experiments'), (4, 'Queries & Analyses');

update `lasauthserver`.`loginmanager_lasmodule` set `menucat_id`=2 where id=1;
update `lasauthserver`.`loginmanager_lasmodule` set `menucat_id`=4 where id=4;
update `lasauthserver`.`loginmanager_lasmodule` set `menucat_id`=1 where id=5;
update `lasauthserver`.`loginmanager_lasmodule` set `menucat_id`=1 where id=9;
update `lasauthserver`.`loginmanager_lasmodule` set `menucat_id`=3 where id=12;
update `lasauthserver`.`loginmanager_lasmodule` set `menucat_id`=4 where id=15;
update `lasauthserver`.`loginmanager_lasmodule` set `menucat_id`=3 where id=16;
update `lasauthserver`.`loginmanager_lasmodule` set `menucat_id`=3 where id=17;
update `lasauthserver`.`loginmanager_lasmodule` set `menucat_id`=4 where id=18;
update `lasauthserver`.`loginmanager_lasmodule` set `menucat_id`=3 where id=19;
update `lasauthserver`.`loginmanager_lasmodule` set `menucat_id`=2 where id=20;



CREATE  TABLE IF NOT EXISTS `lasauthserver`.`loginmanager_lasvideo` (
  `id` INT(11) NOT NULL AUTO_INCREMENT ,
  `title` VARCHAR(100) NOT NULL ,
  `description` VARCHAR(5000),
  `url` VARCHAR(200),
  `rank` int(11),
  `activity` INT(11) NOT NULL,
  PRIMARY KEY (`id`) ,
  CONSTRAINT `fk_lasvideo_activity` FOREIGN KEY (`activity`) REFERENCES `lasauthserver`.`loginmanager_activity`(`id`)
  )
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


insert into `lasauthserver`.`loginmanager_lasvideo` values 
( 2, 'Archive', '', 'video/XMM/archive.ogg', 3, 19),
( 3, 'Change Status', '', 'video/XMM/changeStatus.ogg', 2, 33),
( 4 , 'Manage Groups', '' ,'video/XMM/manageGroups.ogg', 3, 33),
( 5 , 'Finalize Treatments', '', 'video/XMM/finalizeTreat.ogg', 2, 23),
(6 , 'Ongoing' , '', 'video/XMM/ongoing.ogg', 2, 19),
(8 ,  'Create Treatments', '', 'video/XMM/browseCreateTreats.ogg', 1, 23),
( 9, 'Implant Xenografts', '', 'video/XMM/implant.ogg', 1, 20),
( 10, 'Explant Xenografts', '', 'video/XMM/explant.ogg', 1, 21),
( 11, 'Mice Loading' , '', 'video/XMM/miceLoading.ogg', 1, 33),
( 13, 'Review', '', 'video/XMM/review.ogg', 1, 19),
( 18, 'Return', '', 'video/Storage/Return.ogg', 1, 40),
( 23, 'New kit type', '', 'video/Biobank/Kit_type_new.ogg', 1, 11),
( 24, 'New Kit', '', 'video/Biobank/Kit_new.ogg', 2, 11),
( 25, 'Collection archive assign to existent', '', 'video/Biobank/Collect_arch_assign_to_exist.ogg', 3, 28),
( 26, 'Collection - Fresh tissue', '', 'video/Biobank/Collect_fresh_tissue.ogg', 1, 28),
( 27, 'Collection archive new collection', '', 'video/Biobank/Collect_arch_new_collection.ogg', 2, 28),
( 28, 'Plan derivation', '', 'video/Biobank/Derivation_plan.ogg', 1, 10),
( 29, 'Derivation 1 - Select Aliquots', '', 'video/Biobank/Derivation_1_select_aliquots.ogg', 2, 10),
( 30, 'Derivation 2 - Kit', '', 'video/Biobank/Derivation_2_kit.ogg', 3, 10),
( 31, 'Derivate 3 - Measures', '', 'video/Biobank/Derivation_3_measure.ogg', 4, 10),
( 32, 'Derivate 4 - Create derivatives', '', 'video/Biobank/Derivation_4_create.ogg', 5, 10),
( 33, 'Plan Split', '', 'video/Biobank/Split_plan.ogg', 1, 8),
( 34, 'Split', '', 'video/Biobank/Split.ogg', 2, 8),
( 35, 'Plan Transfer', '', 'video/Biobank/Transfer_plan.ogg', 1, 7),
( 36, 'Send Transfer', '', 'video/Biobank/Transfer_send.ogg', 2, 7),
( 37, 'Receive Transfer', '', 'video/Biobank/Transfer_receive.ogg', 3, 7),
( 38, 'Plan Experiment', '', 'video/Biobank/Experiment_plan.ogg', 1, 26),
( 39, 'Confirm Experiment', '', 'video/Biobank/Experiment_confirm.ogg', 2, 26),
( 40, 'Plan Revalue', '', 'video/Biobank/Revalue_plan.ogg', 1, 9),
( 41, 'Execute Revalue', '', 'video/Biobank/Revalue_execute.ogg', 1, 9),
( 42, 'Plan Retrieve', '', 'video/Biobank/Retrieve_plan.ogg', 1, 32),
( 43, 'Execute Retrieve', '', 'video/Biobank/Retrieve_execute.ogg', 1, 32),
( 44, 'Patient', '', 'video/Biobank/Patient.ogg', 1, 29);

