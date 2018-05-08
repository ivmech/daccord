#!/bin/sh

lowercase(){
    echo "$1" | sed "y/ABCDEFGHIJKLMNOPQRSTUVWXYZ/abcdefghijklmnopqrstuvwxyz/"
}

OS=`lowercase \`uname -s\``
# KERNEL=`uname -r`
MACH=`uname -m`

archive_file="release/daccord_${OS}_${MACH}.tgz"
version_file="release/version_${OS}_${MACH}.h"
history_file="release/history_${OS}_${MACH}.txt"

cp -f appversion.h ${version_file}
cp -f History.txt ${history_file}

# Generate the archive
echo "Generating Archive: ${archive_file}..."

if [ -f ${archive_file} ];
then
  rm ${archive_file}
fi
if [ -f ${archive_file}.sha256sum ];
then
  rm ${archive_file}.sha256sum
fi

tar -zcf ${archive_file} daccord daccord.sh install.sh server_cert.pem updatebeta updaterelease History.txt License.txt www/ scripts/ Config/ plugins/ dzVents/

echo "Creating checksum file...";
hash="$(sha256sum ${archive_file} | sed -e 's/\s.*$//')  update.tgz";
echo $hash > ${archive_file}.sha256sum
if [ ! -f ${archive_file}.sha256sum ];
then
        echo "Error creating archive checksum file!...";
        exit 1
fi

echo "Done!...";
exit 0;
