# Risk models compared (fixed before any result)

Additive (prototype):
R = 0.25*BC + 0.20*SS + 0.25*TI + 0.20*CR + 0.10\*HDE

Multiplicative:
Impact = (0.25*BC + 0.20*SS + 0.25*TI) / 0.70
Likelihood = (0.20*CR + 0.10*HDE) / 0.30
R = Impact * Likelihood

Same five official runs, same tie rule (ascending test ID), same fault matrix.
Both formulas were fixed before any APFD value was computed from the second.
BC = business criticality, SS = security sensitivity, TI = transaction
impact, CR = change relevance, HDE = historical defect exposure.
