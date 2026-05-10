## 15.7 Explainability: What It Reveals and What It Cannot

---

*Explainability* in ML refers to techniques that produce human-interpretable accounts of how a model arrived at a specific prediction. Two techniques are particularly relevant for clinical imaging applications: Grad-CAM and SHAP.

**Grad-CAM** — *Gradient-weighted Class Activation Mapping* — is a technique for convolutional neural networks that produces a heatmap highlighting the regions of an input image most influential to the model's prediction. For a chest X-ray classified as pneumonia, a Grad-CAM heatmap shows which regions of the image most strongly activated the pneumonia prediction. When those regions correspond to the lung fields — where pneumonia manifests pathologically — the heatmap provides evidence that the model is attending to clinically relevant features. When the heatmap highlights a corner of the image, or the border text overlaid by the imaging equipment, the model's prediction may be based on spurious correlations rather than genuine pathology.

**SHAP** — *SHapley Additive exPlanations* — is a technique grounded in cooperative game theory that assigns each input feature a contribution score to a particular prediction. For tabular models, it identifies which patient features drove the model's output. For imaging models, SHAP can be applied to superpixels rather than individual pixels, producing a regional contribution map similar in spirit to Grad-CAM but with stronger theoretical grounding in terms of attribution fairness across features.

Both techniques are diagnostic, not corrective. Grad-CAM showing that the model attends to lung fields does not prove the model is reasoning correctly — it shows that these regions are influential, which is consistent with correct reasoning but does not rule out other explanations. Neither technique provides a complete explanation of model behaviour: they explain individual predictions, not the model's overall decision boundary, and they cannot reveal whether the model's behaviour on the test set will generalise to production inputs that differ from the test distribution.

The engineering value of explainability analysis is threefold. First, it provides a sanity check on whether the model's attention aligns with clinical expectations — which can surface distributional artefacts (the model predicting based on equipment watermarks, hospital identifiers embedded in image metadata, or demographic signals that correlate with the label) that standard metrics would not detect. Second, it generates evidence for clinical governance review: a clinician reviewing a model for deployment can examine Grad-CAM maps on representative examples from each class as part of their approval process. Third, it enables targeted investigation of specific failure cases — when the model misclassifies a particular image, explainability analysis can help determine whether the failure reflects a data quality issue, a class ambiguity, or a generalisation failure.

What explainability cannot do is substitute for rigorous evaluation. A model whose Grad-CAM maps look clinically plausible but whose subgroup recall for the normal class is 0.61 is not acceptable. Explainability provides evidence; the evaluation gate provides the criterion.

---
