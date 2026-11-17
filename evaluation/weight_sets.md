# Weight sets for the sensitivity analysis (fixed before any result)

Order: business criticality, security sensitivity, transaction impact,
change relevance, historical defect exposure.

default 0.25, 0.20, 0.25, 0.20, 0.10 (prototype defaults)
A equal 0.20, 0.20, 0.20, 0.20, 0.20
B impact-heavy 0.30, 0.20, 0.30, 0.10, 0.10
C likelihood-heavy 0.15, 0.15, 0.15, 0.35, 0.20

These sets vary the emphasis. They were chosen before computing any APFD or
tau value, and they were not tuned to the fault-detection matrix.
