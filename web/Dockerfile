FROM ubuntu:18.04

RUN export DEBIAN_FRONTEND=noninteractive &&\
    apt-get update &&\
    apt-get install -y apache2 python2.7 python-pip libapache2-mod-evasive libapache2-mod-jk libapache2-mod-wsgi libmysqlclient-dev libpq-dev libmemcached-dev libffi-dev libssl-dev &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/*
RUN mkdir /las-conf

RUN mkdir /virtualenvs

COPY conf/pip-reqs_1.4.txt /las-conf/pip-reqs_1.4.txt
COPY conf/pip_reqs_1.7.txt /las-conf/pip-reqs_1.7.txt

RUN pip install --upgrade pip
RUN pip install virtualenv
RUN pip install virtualenvwrapper
ENV WORKON_HOME /virtualenvs
RUN /bin/bash -c "source /usr/local/bin/virtualenvwrapper.sh \
    && mkvirtualenv venvdj1.4 \
    && workon venvdj1.4 \
    && pip install --default-timeout=100 -r /las-conf/pip-reqs_1.4.txt"

RUN /bin/bash -c "source /usr/local/bin/virtualenvwrapper.sh \
    && mkvirtualenv venvdj1.7 \
    && workon venvdj1.7 \
    && pip install --default-timeout=100 -r /las-conf/pip-reqs_1.7.txt"
    
#COPY las/LASAuthServer /srv/www/LASAuthServer
#COPY las/catissue /srv/www/catissue
#COPY las/storage /srv/www/storage
#COPY las/caxeno /srv/www/caxeno
#COPY las/cellline /srv/www/cellline
#COPY las/caquery /srv/www/caquery
#COPY las/uarray /srv/www/uarray
#COPY las/realTime /srv/www/realTime
#COPY las/sangerLight /srv/www/sangerLight
#COPY las/fingerPrinting /srv/www/fingerPrinting
#COPY las/ngsmanager /srv/www/ngsmanager
#COPY las/clinicalManager /srv/www/clinicalManager
#COPY las/repmanager /srv/www/repmanager
#COPY las/annotationsManager /srv/www/annotationsManager
#COPY las/newAnnotationsManager /srv/www/newAnnotationsManager
#COPY las/analysismanager /srv/www/analysismanager
#COPY las/beaming /srv/www/beaming
#COPY las/digitalPcr /srv/www/digitalPcr

COPY conf/las-ssl.conf /etc/apache2/sites-available/las-ssl.conf
COPY conf/apache2.conf /etc/apache2/apache2.conf
COPY conf/evasive.conf /etc/apache2/mods-available/evasive.conf
COPY conf/fqdn.conf /etc/apache2/conf-available/fqdn.conf

COPY ssl/apache.crt /etc/apache2/ssl/las.crt
COPY ssl/apache.key /etc/apache2/ssl/las.key


RUN rm -rf /etc/apache2/sites-enabled/* &&\
    ln -s /etc/apache2/sites-available/las-ssl.conf /etc/apache2/sites-enabled/las-ssl.conf
RUN ln -sf /etc/apache2/mods-available/headers.load /etc/apache2/mods-enabled/headers.load
RUN ln -sf /etc/apache2/mods-available/proxy.conf /etc/apache2/mods-enabled/proxy.conf
RUN ln -sf /etc/apache2/mods-available/proxy.load /etc/apache2/mods-enabled/proxy.load
RUN ln -sf /etc/apache2/mods-available/proxy_html.conf /etc/apache2/mods-enabled/proxy_html.conf
RUN ln -sf /etc/apache2/mods-available/proxy_html.load /etc/apache2/mods-enabled/proxy_html.load
RUN ln -sf /etc/apache2/mods-available/proxy_http.load /etc/apache2/mods-enabled/proxy_http.load
RUN ln -sf /etc/apache2/mods-available/rewrite.load /etc/apache2/mods-enabled/rewrite.load
RUN ln -sf /etc/apache2/mods-available/socache_shmcb.load /etc/apache2/mods-enabled/socache_shmcb.load
RUN ln -sf /etc/apache2/mods-available/ssl.conf /etc/apache2/mods-enabled/ssl.conf
RUN ln -sf /etc/apache2/mods-available/ssl.load /etc/apache2/mods-enabled/ssl.load
RUN ln -sf /etc/apache2/mods-available/unique_id.load /etc/apache2/mods-enabled/unique_id.load
RUN ln -sf /etc/apache2/mods-available/xml2enc.load /etc/apache2/mods-enabled/xml2enc.load
RUN rm /etc/apache2/mods-enabled/reqtimeout.conf  /etc/apache2/mods-enabled/reqtimeout.load
RUN a2enconf fqdn

RUN ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log

ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid

EXPOSE 443
EXPOSE 80

RUN usermod -u 1000 www-data
RUN usermod -G staff www-data
RUN groupmod -g 1000 www-data

RUN mkdir /las
COPY start.sh /las/start.sh
COPY wait-for-it.sh /las/wait-for-it.sh
RUN cp -r /virtualenvs/venvdj1.4/django/contrib/admin/templates /virtualenvs/venvdj1.4/lib/python2.7/site-packages/django/contrib/auth
CMD ["/las/start.sh"]
