# Response_to_Reviewer_1

We thank the reviewer-for their insightful comments.We address each concern below.

## 1.Experimental_Setup

The reviewer-raises a valid point about the baseline comparisons.We have added results for two additional baselines:

|Method|Accuracy|F1-Score|Runtime|
|------|--------|--------|-------|
|Ours|94.2|91.8|2.3s|
|Base-A|89.1|86.3|5.1s|
|Base-B|91.0|88.5|3.8s|

As shown,our method achieves the best performance across all metrics while maintaining competitive runtime.

## 2.Theoretical_Analysis

The loss function is defined as$L=\frac{1}{N} \sum_{i=1}^{N} \ell(f(x_i),y_i)$,where$f(x_i)$ denotes the model prediction and$y_i$ is the ground truth label.

We prove convergence under the assumption that$\alpha+\beta\leq1$(see Theorem 3).

>**Note:** The full proof is provided in Appendix B of the revised manuscript.

## 3.Related_Work

We have expanded the related work section to include [Smith et al.(2023)][1]and [Jones et al.(2024)](https://example.com/jones2024). We also cite [Lee et al.(2023)][1]which uses the same framework.

## References

[1]:Smith_et_al.,Deep_Learning_for_X,NeurIPS_2023
[2]:Jones_et_al.,Better_Y_with_Z,ICML_2024

[1]:https://example.com/smith2023
