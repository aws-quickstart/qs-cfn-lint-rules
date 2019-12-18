#!/bin/bash

cd /etc/chef; chef-client -z -j chef-client.json
systemctl stop nginx
systemctl disable nginx
yum remove -y nginx
systemctl disable haproxy
systemctl stop haproxy
yum remove -y haproxy
rm -fr /etc/haproxy/haproxy.cfg
rm -fr /var/log/haproxy
systemctl stop mysql-default
systemctl disable mysql-default
systemctl stop tomcat-share
systemctl disable tomcat-share
yum remove -y mysql-server
rm -fr /etc/mysql-default* /var/lib/mysql* /var/log/mysql-default* /usr/lib/systemd/system/mysql-default.service
rm -fr /etc/tomcat-share /var/lib/tomcat-share /usr/share/tomcat-share /var/log/tomcat-share /var/cache/tomcat-share /etc/sysconfig/tomcat-share /usr/lib/systemd/system/tomcat-share.service
rm -fr /etc/chef/chef-client.json
rm -fr /etc/chef/nodes/*.json
chmod 700 /usr/share/tomcat/shared/classes/alfresco-global.properties
rm -fr /etc/chef/replaceValues.sh
rm -fr /etc/chef/run.sh
