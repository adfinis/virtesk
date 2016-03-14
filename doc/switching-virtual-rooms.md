# Amoothei-vdi: Switching virtual rooms

------------------------------------------


## Introduction
Switching the virtual room assigned to a physical set of thinclient (the physical room) is an
important feature of amoothei-vdi.

Uses:

+ **Quality control**: virtual rooms can be tested before assignement to physical rooms.
+ **Dedicated VMs for exams**
+ **Dedicated VMs for special applications**
+ **Win7 Desktops for one lesson, Linux Desktops for next lessons** 
    + Thinclients can dispaly Linux VMs, however, no rollout tools for Linux desktops have been implemented in amoothei-vdi so far.
+ ...

## Database
Switching virtual rooms is implemented using the postgres database. 

Documentation:

+ [Database layout](tc-vm-mapping.md)
+ [Database Installation + DB Access](amoothei-infrastructure-server.md#setting-up-postgres-database)
+ [Defining virtual rooms](amoothei-vm-rollout-config.md#room-definitions-section-room-room01)

## How to switch virtual rooms
### How to switch virtual rooms: simple cases
For a single TC, the assigned VM can be changed like this:

```
psql -U vdi-dbadmin -h localhost vdi -c "
	UPDATE timed_thinclient_to_vm_mapping \
	SET vm='test01-vd01' WHERE thinclient='test01-tc01' \
	AND start_date IS NULL AND end_date IS NULL;"
```
Output:
```
UPDATE 1
```

It might be convinient to use an SQL-File for this:

update.sql:
```
UPDATE timed_thinclient_to_vm_mapping SET vm='test01-vd01' WHERE thinclient='test01-tc01' AND start_date IS NULL AND end_date IS NULL;
UPDATE timed_thinclient_to_vm_mapping SET vm='test01-vd02' WHERE thinclient='test01-tc02' AND start_date IS NULL AND end_date IS NULL;
UPDATE timed_thinclient_to_vm_mapping SET vm='test01-vd03' WHERE thinclient='test01-tc03' AND start_date IS NULL AND end_date IS NULL;
```

Executing update.sql:
```
psql -U vdi-dbadmin -h localhost vdi < room.sql
UPDATE 1
UPDATE 1
UPDATE 1
```

If you want to assign the VMs `test02-vd*` instead of `test01-vd*`, then you can use `vim` or `sed` for changeing update.sql:

Using vim:
```
vim update.sql                                # Open file with vim
:%s/test01-vd/test02-vd/                      # Apply regex over whole file
:wq                                           # Write file, quit
```

Using sed:
```
sed -i 's/test01-vd/test02-vd/' update.sql
```

The exact regexes needed for your environment do depend on your naming schema; In general, switching virtual rooms is alot easier when systematic naming is used.

Please note that all examples only update records where start_date/end_date are NULL. This is useful for most cases, but it might need adjustment for special cases.

### How to switch virtual rooms: advanced examples
When changeing the assigned VMs for 300 thinclients (10 physical rooms with up to 30 thinclients each), then bash comes handy to generate the SQL statements:

generatesql-statements.sh (available in `sample_config/`):
```
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
```

Please adjust `ROOMS="test01 test02 ...` and `TC_NAME="${ROOM}-tc${ID_TWODIGIT}"` and `VM_NAME="${ROOM}-vd${ID_TWODIGIT}"` according to your naming scheme, and `IDs=$(seq 1 30)` according to the number
of TCs in your rooms. Some rooms might have less than 30 thinclients - however, the generated SQL statements for the non-existing
TCs won't hurt, and its easier to process all rooms in an uniform way.

Running it directly:
```
bash generatesql-statements.sh | psql -U vdi-dbadmin -h localhost vdi 
```

Putting SQL commands into a file first, and run them afterwards:

```
bash generatesql-statements.sh > update.sql            # Generate SQL statements
less update.sql                                        # Control SQL statements
psql -U vdi-dbadmin -h localhost vdi < update.sql      # Execute SQL statements
```

The same bash script can be used to generate the mapping for new thinclients - only the SQL statement needs to be replaced:

```
INSERT INTO timed_thinclient_to_vm_mapping (vm, thinclient) 
VALUES ('${VM_NAME}', '${TC_NAME}');
```

