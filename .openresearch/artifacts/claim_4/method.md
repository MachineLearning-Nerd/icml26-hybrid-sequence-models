# Claim 4 method

## Non-circular window calibration

For each \(W\in\{2,4,8,16,32,64\}\), the checker performs monotone doubling followed by exact binary search over integer context windows. At each candidate it computes the exact rational success probability, not a tolerance-based simulation. The selected \(K\) is the first hit at 99%; \(K-1\) must remain below 99%.

The inequality \(-\log(1-1/W)\ge1/W\) gives \(K\le\lceil W\log100\rceil+1\), so the calibrated window is \(O(W)\), stronger than the claimed \(\widetilde O(|\mathcal V|)\).

## Three-layer construction

The Mamba state shifts in exactly \(\log_2W\) query bits. All possible prefixes number \(1+2+\cdots+W=2W-1=O(|\mathcal V|)\).

The first attention layer has a hard previous-position mask and forms `(previous token, current token)` pairs. The second compares the decoded query's signed binary code with each previous-token code and adds a bounded increasing positional bias. Match/non-match score separation exceeds the entire bias range, while recency strictly orders repeated matches. A finite temperature makes the last match's softmax mass greater than 1/2, preserving every coordinate of the successor token code for exact linear decoding.

For \(W=2\), the checker exhausts every query and all \(2^7\) contexts: absent queries count as failures. For larger vocabularies, exact integer counts establish the distributional probability and adversarial direct cases cover earliest, latest, and repeated query occurrences.

## Negative control

At \(W=2\), the calibrated first hit is \(K=7\). Reducing to \(K=6\) gives \(63/64=0.984375<0.99\), so the checker exits 9.
