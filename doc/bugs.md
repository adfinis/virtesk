# Amoothei-VDI: Known bugs

----------------------

## Harmless bugs
### VMSnapshotCdroms object comparison caused infinite loop [uncritical]

Error messages while rolling out a virtual room:

```
2016-01-20 19:27:14,186 - root - DEBUG - Creating a snapshot(description: Automatic snapshot after amoothei-vmrollout, IP=XXXXXXXXXXXX, scripttime=2016-01-20-1853)  of vm test03-vd01... done
2016-01-20 19:27:15,141 - root - DEBUG - Creating a snapshot(description: Automatic snapshot after amoothei-vmrollout, IP=XXXXXXXXXXXX, scripttime=2016-01-20-1853)  of vm test03-vd03... done
VMSnapshotCdroms object comparison caused infinite loop.
2016-01-20 19:27:16,034 - root - DEBUG - Creating a snapshot(description: Automatic snapshot after amoothei-vmrollout, IP=XXXXXXXXXXXX, scripttime=2016-01-20-1853)  of vm test03-vd05... done
VMSnapshotCdroms object comparison caused infinite loop.
VMSnapshotCdroms object comparison caused infinite loop.
2016-01-20 19:27:17,363 - root - DEBUG - Creating a snapshot(description: Automatic snapshot after amoothei-vmrollout, IP=XXXXXXXXXXXX, scripttime=2016-01-20-1853)  of vm test03-vd07... done
VMSnapshotCdroms object comparison caused infinite loop.
VMSnapshotCdroms object comparison caused infinite loop.
VMSnapshotCdroms object comparison caused infinite loop.
2016-01-20 19:27:18,254 - root - DEBUG - Creating a snapshot(description: Automatic snapshot after amoothei-vmrollout, IP=XXXXXXXXXXXX, scripttime=2016-01-20-1853)  of vm test03-vd09... done
VMSnapshotCdroms object comparison caused infinite loop.
VMSnapshotCdroms object comparison caused infinite loop.
VMSnapshotCdroms object comparison caused infinite loop.
VMSnapshotCdroms object comparison caused infinite loop.
2016-01-20 19:27:19,231 - root - DEBUG - Creating a snapshot(description: Automatic snapshot after amoothei-vmrollout, IP=XXXXXXXXXXXX, scripttime=2016-01-20-1853)  of vm test03-vd11... done
VMSnapshotCdroms object comparison caused infinite loop.
VMSnapshotCdroms object comparison caused infinite loop.
VMSnapshotCdroms object comparison caused infinite loop.
VMSnapshotCdroms object comparison caused infinite loop.
VMSnapshotCdroms object comparison caused infinite loop.
2016-01-20 19:27:22,519 - root - DEBUG - Creating a snapshot(description: Automatic snapshot after amoothei-vmrollout, IP=XXXXXXXXXXXX, scripttime=2016-01-20-1853)  of vm test03-vd15... done
```

Cause: unknown. Maybe a python phaenomen related to recursive object structures, like described in [https://mail.python.org/pipermail/python-dev/2003-October/039445.html](https://mail.python.org/pipermail/python-dev/2003-October/039445.html)?

Impact: **none**, the VMs and the snapshots are created successfully.
