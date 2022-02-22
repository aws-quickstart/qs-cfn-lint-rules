#!/bin/bash
set -x

# On all sas nodes
echo "$HOSTNAME"

sudo -u root bash << EOF
if ! grep -q "@sas" /etc/security/limits.conf; then
    echo "@sas             hard    nofile         20480" >> /etc/security/limits.conf
    echo "@sas             soft    nofile         20480" >> /etc/security/limits.conf
    echo "@sas             hard    nproc          20480" >> /etc/security/limits.conf
    echo "@sas             soft    nproc          20480" >> /etc/security/limits.conf
fi

if ! grep -q "SASFoundation" /etc/profile; then
    echo ". /sas/lsf/conf/profile.lsf" >> /etc/profile
    echo 'export PATH=$PATH:/usr/local/SASHome/SASFoundation/9.4' >> /etc/profile
fi

if ! grep -q "ulimit" /home/sasinst/.bash_profile; then
    echo "ulimit -n 20480" >> /home/sasinst/.bash_profile
    echo "ulimit -u 20480" >> /home/sasinst/.bash_profile
fi

cd /usr/local
mkdir SASHome config metadata
chmod 755 SASHome config metadata
chown sasinst:sas SASHome config metadata
rm -Rf SASHome/* config/* metadata/*
pkill -U sasinst
exit
EOF

sudo -u sasinst bash << EOF
cd /sas/$1
./setup.sh -deploy -quiet -responsefile /sas/quickstart/playbooks/templates/metadata_install.txt
exit
EOF

sudo -u root bash << EOF
/usr/local/SASHome/SASFoundation/9.4/utilities/bin/setuid.sh
exit
EOF

sudo -u sasinst bash << EOF
cd /sas/$1
./setup.sh -deploy -quiet -responsefile /sas/quickstart/playbooks/templates/metadata_config.txt
exit
EOF
