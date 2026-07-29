# Historical baseline method

This node does not attempt to verify a paper claim. It freezes and machine-checks the inputs from which later claim nodes will descend:

1. exact repository baseline SHA;
2. explicit-User-Agent paper retrieval hashes and theorem anchors;
3. exact judged Space revision and a 13-file SHA-256 manifest;
4. live verdict selected by exact `space_id`;
5. comparison logbook organization and evidence gaps;
6. fixed `uv` command and Python 3.12 lock input.

The cumulative runner validates these records and launches a negative-control subprocess that mutates the protected manifest in memory. The control must exit nonzero.

