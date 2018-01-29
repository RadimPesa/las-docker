delimiter //

drop trigger if exists audit_aliquot;
create trigger audit_aliquot
before insert on aliquot_audit
for each row
begin
if new._audit_change_type= 'I' then
select id into @aliq_id
from aliquot
where aliquot.uniqueGenealogyID= new.uniqueGenealogyID;
set new.id=@aliq_id;
END if;
END; //

delimiter ;



delimiter //

drop trigger if exists audit_kit;
create trigger audit_kit
before insert on kit_audit
for each row
begin
if new._audit_change_type= 'I' then
select id into @id
from kit
where kit.barcode= new.barcode and kit.idKitType=new.idKitType;
set new.id=@id;
END if;
END; //

delimiter ;

delimiter //

drop trigger if exists audit_derivation;
create trigger audit_derivation
before insert on aliquotderivationschedule_audit
for each row
begin
if new._audit_change_type= 'I' then
select id into @id
from aliquotderivationschedule
where aliquotderivationschedule.idAliquot= new.idAliquot and aliquotderivationschedule.idDerivationSchedule=new.idDerivationSchedule and aliquotderivationschedule.idDerivedAliquotType=new.idDerivedAliquotType and derivationExecuted=0 and deleteTimestamp is null;
set new.id=@id;
END if;
END; //

delimiter ;

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

