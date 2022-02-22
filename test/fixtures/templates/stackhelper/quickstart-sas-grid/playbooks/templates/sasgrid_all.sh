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
    echo 'export PATH=$PATH:/sas/SASHome/SASFoundation/9.4' >> /etc/profile
fi

if ! grep -q "profile.lsf" /etc/profile; then
    echo ". /sas/lsf/conf/profile.lsf" >> /etc/profile
fi

if ! grep -q "ulimit" /home/sasinst/.bash_profile; then
    echo "ulimit -n 20480" >> /home/sasinst/.bash_profile
    echo "ulimit -u 20480" >> /home/sasinst/.bash_profile
fi

exit
EOF
