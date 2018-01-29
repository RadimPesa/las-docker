delimiter //

create trigger audit_container
before insert on container_audit
for each row
begin
if new._audit_change_type= 'I' then
select id into @container_id
from container
where container.barcode= new.barcode;
set new.id=@container_id;
END if;
END; //

delimiter ;


delimiter //

drop trigger if exists audit_aliqstorage;
create trigger audit_aliqstorage
before insert on aliquot_audit
for each row
begin
if new._audit_change_type= 'I' then
select id into @aliq_id
from aliquot
where aliquot.genealogyID= new.genealogyID and aliquot.endTimestamp is null;
set new.id=@aliq_id;
END if;
END; //

delimiter ;

create view currentaliquot as select * from aliquot where endTimestamp is null;