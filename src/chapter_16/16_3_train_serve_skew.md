## 16.3 Train/Serve Skew

---

Train/serve skew is the condition in which the data transformation applied to inputs at serving time differs from the transformation applied to the same inputs during training. It is one of the most common production ML application failures, and it is entirely self-inflicted.

### 16.3.1 How Train/Serve Skew Happens

The typical path to train/serve skew is duplication. A data scientist writes preprocessing code in a training notebook. When the serving API is built, a developer rewrites the preprocessing logic independently — because the notebook is not easily importable, because the frameworks differ, or because the person building the API does not have access to the original code. The two implementations look similar, but differ in a detail: one applies normalisation before resizing, the other after. One converts the image to RGB before normalising, the other assumes greyscale. One uses bilinear interpolation for resizing, the other uses nearest-neighbour.

The model was trained on data that was normalised with ImageNet statistics: mean [0.485, 0.456, 0.406] and standard deviation [0.229, 0.224, 0.225] applied per channel after resizing to 224×224 and converting to a float tensor in the range [0, 1]. If the serving API normalises with different values — or applies the same values in a different order — the model receives inputs whose pixel distribution it has never seen during training. The predictions it generates are not entirely random, because the model has learned some features that are robust to this shift. But they are degraded in a way that is invisible without ground truth labels to compare against.

Breck et al. documented train/serve skew as one of the most impactful categories of ML production failure in their survey of ML systems at Google, noting that it often went undetected for extended periods precisely because the model continued to return plausible-looking predictions ([Breck et al., 2017](https://doi.org/10.1109/BigData.2017.8258038)).

### 16.3.2 The Shared Module Pattern

The correct architectural response to train/serve skew is to define preprocessing as code in a single shared module, imported by both the training pipeline and the serving API. There is no separate implementation for serving. There is one implementation, shared.

For the ChestScan application, the transforms are defined in a single `transforms.py` module. The training pipeline imports `get_val_transforms()` from this module. The FastAPI backend imports the same function from the same file. The file is physically copied into the serving container as part of the Docker build step. There is no possibility of the two implementations diverging, because there are not two implementations.

The shared module must also encapsulate the normalisation parameters — the mean and standard deviation values derived from the training dataset distribution. These are not arbitrary constants. If the training data changes (a new dataset version is registered), the normalisation parameters may change, and the shared module must be updated to reflect this. The normalisation parameters and the model weights are co-versioned artefacts: a model trained with one set of parameters cannot be correctly served with another.

---
