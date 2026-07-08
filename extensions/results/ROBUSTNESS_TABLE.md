# Locked robustness package (hash 8a6087341e)

All models: position + story FE, cluster-robust SE by sent_uid, z-scored predictors (ddof=0). Wake models control for entropy, curvature, surprisal, tee3_perp/par, ctee_m5, length, freq. RT models control for fine TEE channels, surprisal, lexical, punct, prev-RT, at L0 and L1.

| claim               | variant                           | L1                       | L5                       | L10                      | L0                       |
|:--------------------|:----------------------------------|:-------------------------|:-------------------------|:-------------------------|:-------------------------|
| ntee wake           | punct-controlled (all)            | +0.204 (p=2e-14)* n=1627 | +0.168 (p=4e-10)* n=1627 | +0.150 (p=8e-08)* n=1627 | nan                      |
| ntee wake           | punct-free                        | +0.182 (p=9e-11)* n=1414 | +0.154 (p=3e-07)* n=1414 | +0.124 (p=2e-05)* n=1414 | nan                      |
| ntee wake           | held-out clustering (punct-free)  | +0.186 (p=8e-12)* n=1414 | +0.115 (p=2e-05)* n=1414 | +0.093 (p=9e-04)* n=1414 | nan                      |
| ntee wake           | k=30 (punct-free)                 | +0.104 (p=3e-04)* n=1414 | +0.096 (p=4e-04)* n=1414 | +0.084 (p=7e-03)* n=1414 | nan                      |
| ntee wake           | k=300 (punct-free)                | +0.159 (p=3e-07)* n=1414 | +0.123 (p=3e-04)* n=1414 | +0.080 (p=1e-02)* n=1414 | nan                      |
| ntee wake           | no punct in w+1..w+5 (punct-free) | +0.110 (p=1e-02)* n=701  | +0.145 (p=2e-03)* n=701  | +0.125 (p=4e-03)* n=701  | nan                      |
| wake L5 competitors | tee3_perp                         | nan                      | -0.066 (p=5e-02) n=1414  | nan                      | nan                      |
| wake L5 competitors | tee3_par                          | nan                      | -0.021 (p=4e-01) n=1414  | nan                      | nan                      |
| wake L5 competitors | ctee_m5                           | nan                      | -0.016 (p=6e-01) n=1414  | nan                      | nan                      |
| wake L5 competitors | nswitch_k100                      | nan                      | +0.070 (p=8e-04)* n=1414 | nan                      | nan                      |
| wake L5 competitors | curvature_3                       | nan                      | -0.023 (p=4e-01) n=1414  | nan                      | nan                      |
| wake L5 competitors | entropy                           | nan                      | +0.040 (p=2e-01) n=1414  | nan                      | nan                      |
| wake L5 competitors | surprisal                         | nan                      | +0.064 (p=3e-02)* n=1414 | nan                      | nan                      |
| ntee on-word RT     | punct-controlled (all)            | nan                      | nan                      | nan                      | +0.002 (p=8e-05)* n=9830 |
| ntee on-word RT     | punct-free                        | nan                      | nan                      | nan                      | +0.002 (p=7e-04)* n=8667 |
| ntee on-word RT     | held-out (punct-free)             | nan                      | nan                      | nan                      | +0.002 (p=2e-03)* n=8667 |
| ntee on-word RT     | k=30 (punct-free)                 | nan                      | nan                      | nan                      | +0.001 (p=9e-03)* n=8667 |
| ntee on-word RT     | k=300 (punct-free)                | nan                      | nan                      | nan                      | +0.002 (p=2e-02)* n=8667 |
| ntee on-word RT     | NULL: ctee_m5 (punct-free)        | nan                      | nan                      | nan                      | +0.000 (p=1e+00) n=8667  |
| ntee on-word RT     | NULL: nswitch (punct-free)        | nan                      | nan                      | nan                      | -0.002 (p=3e-03)* n=8667 |