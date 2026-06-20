# Voxel Clustering Pipeline

## Table of Contents
1. [Scientific Background](#1-scientific-background)
2. [Why K-Means](#2-why-k-means)
3. [Data Construction](#3-data-construction)
4. [Experiments & Conditions](#4-experiments--conditions)
5. [Analysis Workflow](#5-analysis-workflow)
6. [Results Summary](#6-results-summary)
7. [End-to-End Run Order](#7-end-to-end-run-order)
8. [Script & Notebook Reference](#8-script--notebook-reference)

---

## 1. Scientific Background

The language network in the left hemisphere responds more strongly to sentences than to lists of unconnected words or nonwords. The standard regional-level finding is a graded profile written **S > W > J > N** (Sentences > Words > Jabberwocky > Nonwords). The motivating question for this work is whether that single regional profile hides functionally distinct sub-populations of voxels — in particular, whether some voxels track lexical meaning, some track syntactic structure, and some track compositional/sentence-level meaning, even though the region as a whole shows one blended response.

Earlier region-level conjunction analyses (MATLAB `spm_ss` toolbox) tried to isolate syntax-selective (J>N but not W>N) and lexical-selective (W>N but not J>N) responses directly, and largely failed: focusing on voxels without a W>N effect left no voxels with a clean syntax effect, and vice versa. That negative result motivated the move to a **model-free, voxel-level clustering approach** — rather than imposing contrasts, let the voxels group themselves by response shape and see whether interpretable sub-populations emerge.

---

## 2. Why K-Means

K-means was chosen as the primary algorithm for pragmatic rather than theoretical reasons:

- **Simple and model-free.** Imposes no prior structure — appropriate for an exploratory search where the goal is to discover whether sub-populations exist, not to confirm a pre-specified model.
- **Interpretable.** Produces a direct, hard voxel-to-cluster mapping. Every voxel gets exactly one label, making downstream questions ("which fROI does this cluster come from?", "what is this cluster's response profile?") trivial to ask.
- **Comparable across alternatives.** Hierarchical and spectral clustering were both tested. Hierarchical preserved similar profiles; spectral did not and was judged less suitable for fMRI data.

### Known Limitation

K-means relies on Euclidean distance, making it sensitive to overall response magnitude. A recurring concern is that clusters may differ mainly in amplitude while sharing the same S>W>J>N shape. Two mitigations are discussed:
1. **Per-voxel mean normalization** — subtracting each voxel's mean across conditions to remove magnitude.
2. **Correlation- or cosine-based methods** — e.g. K-medoids on a cosine-distance matrix.

Notably, mean-normalization did not collapse the magnitude clusters as expected, which was treated as a puzzling and informative finding in its own right.

---

## 3. Data Construction

Each voxel becomes a **vector of condition responses**, and clustering runs over the pooled bag of voxels from all subjects.

1. **Localize.** For each subject, use their individual language localizer (a separate S > N contrast, "langloc") to select the **top 10% most language-responsive voxels** within each language parcel. This subject-specific fROI approach ensures every voxel entering the analysis is genuinely language-responsive, defined independently of the critical experiment.

2. **Restrict to 5 core LH parcels.** Use only: **LAntTemp, LPostTemp, LIFGorb, LIFG, LMFG** — dropping the LH AngG parcel and all right-hemisphere parcels. Rationale: there is known functional separation between LH lang fROIs, RH lang fROIs, and bilateral AngG, so mixing them would pool functionally different networks. (One right-lateralized outlier subject is the documented exception where RH parcels are substituted.)

3. **Extract condition estimates.** For each selected voxel, read its response (a beta/contrast estimate from `con_XXXX.nii`, not a t-map) to each experimental condition from the first-level GLM. Effect sizes are used rather than t-statistics for interpretability; results were near-identical either way.

4. **Pool.** Stack every subject's voxels into one big **(voxels × conditions)** matrix. For ~11–16 subjects this is on the order of 10⁶ voxel-vectors. Each voxel's fROI of origin and subject are tracked throughout.

---

## 4. Experiments & Conditions

### SWJN Family (`clustering_orig_swjn.ipynb`)

Experiments: `SWJN_deluxe`, `SWJNV2`, `Nlength_con2`, `ParamNew`

Conditions are defined by linguistic level. The **4 shared conditions** used as the clustering basis (so profiles can be compared across datasets):

| Code | Condition    | What it isolates                              |
|------|--------------|-----------------------------------------------|
| S    | Sentences    | structure + lexical meaning + composition     |
| W    | Word lists   | lexical meaning, no structure                 |
| J    | Jabberwocky  | structure, no lexical meaning                 |
| N    | Nonword lists| neither (low-level baseline)                  |

Additional conditions (e.g. NS, BS) exist in some datasets and are **plotted but not clustered on** — they probe the resulting clusters with held-out conditions. This "cluster on 4, plot on 6" design is implemented directly in `clustering_orig_swjn.ipynb`.

### SyntCat (`clustering_syntcat.ipynb`)

Clusters by **part-of-speech category** rather than sentence/word/jabberwocky/nonword. The 18 raw columns (POS × frequency-band combinations) are collapsed into 5 POS conditions:

| Code | Category      |
|------|---------------|
| N    | Noun          |
| AJ   | Adjective     |
| V    | Verb          |
| AV   | Adverb        |
| FW   | Function word |

The clustering vector is 5-dimensional (one value per POS class). Pipeline mechanics are identical to SWJN; only the meaning of the condition axis changes.

---

## 5. Analysis Workflow

### 5.1 Sanity Checks

- **Column-mean profile.** Average each condition across all pooled voxels and plot with SEM-over-participants error bars. Should reproduce the expected profile (S>W>J>N for SWJN). If not, something upstream is broken.
- **Per-subject similarity to the group.** For each subject, correlate their condition profile against the mean of the others (one r per subject). Flags anomalous participants — e.g. a right-lateralized subject whose word-list response was abnormally low (handled by switching to RH parcels).

### 5.2 Choosing K

Two diagnostics:
- **Elbow method** — within-cluster sum of squares vs. K
- **Silhouette scores**

K=2 is mathematically optimal by most metrics; K=3–K=6 are all defensible. **K=4** was used for most SWJN work as a compromise capturing finer structure than the "too coarse" K=2; K=2 and K=6 were run as robustness checks. A gap-statistic implementation is available in `utils/gapstatistics_calc.py`.

### 5.3 Cluster Visualizations

Four core plot families interpret the result:

1. **Cluster response profiles.** Mean response to each condition per cluster (SEM over participants). Reveals whether a cluster has a distinctive shape — e.g. an S>everything "compositional" profile vs. the standard graded profile.

2. **Cluster composition / fROI proportions (both directions).**
   - For each cluster: what proportion of its voxels comes from each of the 5 fROIs.
   - For each fROI: what proportion of its voxels falls into each cluster.
   Proportions (not raw counts) control for differing fROI sizes; computed per-subject then averaged with SEM. This is the basis for spatial claims (e.g. AntTemp/PostTemp contributing most to the "interesting" cluster).

3. **Cluster sizes.** Mean voxel count per cluster with SEM over subjects.

4. **Per-fROI profiles within a cluster.** Response profile broken out by fROI (regions × conditions grid). Frontal-region hints of syntax (S>J>others in IFG/IFGorb) were spotted here.

---

## 6. Results Summary

The bottom line from the SWJN arc is a **robust null with respect to the original hypothesis**. Across `SWJN_deluxe`, `SWJNV2`, and `Nlength_con2` — and a combined n=88 "mega" analysis — clusters reproduced the same S>W>J>N shape, differing mainly in **overall magnitude** (ordering by amplitude: high/med/low/int). No stable, clean dissociation of syntax from lexical semantics emerged at the voxel level. Profiles replicated strongly across datasets and across K — strong replicability, but of a single blended pattern rather than the hoped-for functional sub-types.

---

## 7. End-to-End Run Order

1. **(MATLAB)** Generate 5-parcel LH locT masks for all subjects using `toolbox/toolbox_mroi_only_for_creating_LH_parceled_locTs_SyntCat.m` (or equivalent for your experiment).

2. **Set `EXPT_NAME` / `LOC_NAME`** and the subjects CSV in `data_prep.py`, then run:
   ```bash
   python data_prep.py
   ```
   Outputs: masked per-contrast `.npy` files + `froi_map.npy` per subject.

3. **Run `assemble_matrix.py`** to build per-subject (voxels × conditions) matrices:
   ```bash
   python assemble_matrix.py
   ```

4. **Open the relevant notebook:**
   - **SWJN datasets** → `clustering_orig_swjn.ipynb`
     - Set: `datasets`, `condition_included=4`, `optimal_k`, odd/even matching
   - **SyntCat** → `clustering_syntcat.ipynb`
     - Set: `expt_name`, `full_column_names`, `n_participant`, `conditions_for_clustering`, `optimal_k`

5. Run in order: **sanity checks → K-selection → cluster → edit `cluster_label_mapping` → generate four plot families.**

---

## 8. Script & Notebook Reference

### `data_prep.py`

Processes individual subject-level fMRI contrast maps (`con_XXXX.nii`) for a defined experiment. Extracts voxel-level data within subject-specific fROIs defined by a language localizer and saves them for downstream clustering.

**Input Files Example**

| Input | Value |
|-------|-------|
| Experiment | `SyntCat` |
| Language localizer | `langlocSN` |
| Subjects CSV | `clustering/subjects/subjects_SyntCat.csv` (maps SyntCat IDs → langlocSN IDs) |
| Individual language ROI mask | `locT_0003_percentile-ROI-lev4b7cdb1c61ede34200a74effa2c31c98.nii` (top 10% lang parcel) |
| Pop-level parcel map | `LH_allParcels_language_noAngG.nii` |

**Output Files**

| Directory | Description |
|-----------|-------------|
| `{EXPT}/temp_data/data_all_runs/` | Raw `con_XXXX.nii` contrast files copied from subjects |
| `{EXPT}/temp_data/clean_data_all_runs/` | Processed `.npy` files containing masked voxels from language fROIs |
| `froi_map.npy` | Array mapping each extracted voxel to its fROI ID |

---

### `assemble_matrix.py`

Constructs subject-level **voxel-by-contrast matrices** from the masked `.npy` files produced by `data_prep.py`. Each subject's per-contrast `.npy` files are stacked into a 2D matrix (voxels × contrasts) and saved to `{EXPT}/clean_matrix_all_runs/`.

---

### `clustering_{EXPT}.ipynb`

Main clustering notebook — customize for each experiment.

**Inputs**
- `{EXPT}/clean_matrix_all_runs/<subject>.npy` — voxel-by-contrast matrices
- `{EXPT}/clean_matrix_all_runs/<subject>_froi_map.npy` — fROI index maps

**Steps**
1. Load and pool voxel matrices across subjects
2. Sanity checks (NaN audit, mean contrast profile, per-subject correlation with group mean)
3. K-means clustering (elbow graph → choose K → fit)
4. Visualize: response profiles, fROI composition, cluster sizes, per-fROI profiles within cluster
