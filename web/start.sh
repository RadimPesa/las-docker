#!/bin/sh

# This script will carry out all of the operations that will prepare the instance
# for running on the current host

# wait for mysql to be ready then populate annotations tables (will skip import if not first run)
/las/wait-for-it.sh lasmysql:3306 -s -t 86400 -- /srv/www/newAnnotationsManager/scripts/populate_tables.sh
# set administrator password
/las/wait-for-it.sh lasmysql:3306 -s -t 86400 -- /srv/www/LASAuthServer/set_admin_password.sh


# create fqdn.conf
echo "Servername ${HOST}" > /etc/apache2/conf-enabled/fqdn.conf
echo "Define FQDN ${HOST}" >> /etc/apache2/conf-enabled/fqdn.conf
# run Apache
/usr/sbin/apache2ctl -D FOREGROUND
