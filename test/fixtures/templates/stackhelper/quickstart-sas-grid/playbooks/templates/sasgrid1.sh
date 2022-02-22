#!/bin/bash
set -x

# On all sas nodes
echo "$HOSTNAME"

sudo -u root bash << EOF
cd /sas
mkdir SASHome config metadata
chmod 755 SASHome config metadata
chown sasinst:sas SASHome config metadata
rm -Rf SASHome/* config/* metadata/*
pkill -U sasinst
exit
EOF

sudo -u sasinst bash << EOF
cd /sas/$1
./setup.sh -deploy -quiet -responsefile /sas/quickstart/playbooks/templates/grid1_install.txt
exit
EOF

sudo -u root bash << EOF
/sas/SASHome/SASFoundation/9.4/utilities/bin/setuid.sh
exit
EOF

sudo -u sasinst bash << EOF
cd /sas/$1
. /sas/lsf/conf/profile.lsf
./setup.sh -deploy -quiet -responsefile /sas/quickstart/playbooks/templates/grid1_config.txt
./setup.sh -deploy -quiet -responsefile /sas/quickstart/playbooks/templates/studio_config.txt
exit
EOF

sudo -u root bash << EOF
echo '-WORK /saswork' >> /sas/SASHome/SASFoundation/9.4/nls/en/sasv9.cfg
. /sas/lsf/conf/profile.lsf
/sas/SASHome/SASFoundation/9.4/utilities/bin/setuid.sh
. /sas/studioconfig/sasstudio.sh start
exit
EOF
