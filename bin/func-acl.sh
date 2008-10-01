#!/bin/sh
id $1 > /dev/null;
if [ $? == 0 ]; then
    setfacl -d -R -m "u:$1:rX" /etc/pki/certmaster/
    setfacl -R -m "u:$1:rX" /etc/pki/certmaster/
    setfacl -d -R -m "u:$1:rwX" /var/lib/func
    setfacl -R -m "u:$1:rwX" /var/lib/func
fi
