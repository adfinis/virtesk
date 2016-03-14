#!/bin/bash

ROOMS="test01 test02 test03 test04 test05 test06 test07 test08 test09 test10"

for ROOM in $ROOMS; do
    IDs=$(seq 1 30)
    echo "# Room ${ROOM}"
    for ID in ${IDs}; do
        ID_TWODIGIT=$(printf "%02d" ${ID})
        TC_NAME="${ROOM}-tc${ID_TWODIGIT}"  
        VM_NAME="${ROOM}-vd${ID_TWODIGIT}" 
        cat <<-ENDofSQL
UPDATE timed_thinclient_to_vm_mapping 
SET vm='${VM_NAME}' WHERE thinclient='${TC_NAME}'
AND start_date IS NULL AND end_date IS NULL;

ENDofSQL
    done
    echo
done

