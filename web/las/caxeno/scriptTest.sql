insert into auth_permission (codename,content_type_id,name) values('can_view_register_mice','29', 'Register Mice');
insert into auth_permission (codename,content_type_id,name) values('can_view_change_status','29', 'Change Status');
insert into auth_permission (codename,content_type_id,name) values('can_view_perform_qualitative','29', 'Perform Qualitative');
insert into auth_permission (codename,content_type_id,name) values('can_view_perform_quantitative','29', 'Perform Quantitative');
insert into auth_permission (codename,content_type_id,name) values('can_view_implant_xenografts','29', 'Implant Xenografts');
insert into auth_permission (codename,content_type_id,name) values('can_view_explant_xenografts','29', 'Explant Xenografts');
insert into auth_permission (codename,content_type_id,name) values('can_view_finalize_treatments','29', 'Finalize Treatments');
insert into auth_permission (codename,content_type_id,name) values('can_view_manage_treatments','29', 'Manage Treatments');
insert into auth_permission (codename,content_type_id,name) values('can_view_new_measurements','29', 'New Measurements');          
           

CREATE TABLE `xenopatients_member` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY
)
;

