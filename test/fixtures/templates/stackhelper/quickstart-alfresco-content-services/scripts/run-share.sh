#!/bin/bash

cd /etc/chef; chef-client -z -j chef-client.json
systemctl stop mysql-default
systemctl disable mysql-default
yum remove -y mysql-server
rm -fr /etc/mysql-default* /var/lib/mysql* /var/log/mysql-default* /usr/lib/systemd/system/mysql-default.service
service solr stop
chkconfig --del solr
rm -rf /opt/alfresco-search-services /var/solr /etc/init.d/solr /etc/sysconfig/solr /var/log/solr /etc/default/solr.in.sh
userdel -r solr
rm -fr /etc/chef/chef-client.json
rm -fr /etc/chef/nodes/*.json
chmod 700 /usr/share/tomcat/shared/classes/alfresco-global.properties
chmod 700 /usr/share/tomcat/shared/classes/alfresco/web-extension/share-cluster-application-context.xml
rm -fr /etc/chef/replaceValues.sh
rm -fr /etc/chef/run.sh
systemctl restart tomcat-alfresco
