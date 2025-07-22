# `data_prep.py`

This script processes individual subject-level fMRI contrast maps (`con_XXXX.nii`) for any defined experiment. It extracts voxel-level data within subject-specific functional ROIs (fROIs) defined by any defined localizer and saves them for downstream clustering analysis.

## Input Files Example

- **Experiment Name**: `SyntCat`
- **Language Localizer**: `langlocSN`
- **Subjects CSV**:  
  `clustering/subjects/subjects_SyntCat.csv`  
  → Contains subject IDs for both `SyntCat` and `langlocSN`

- **Individual language ROI mask**:  
  Top 10% language parcel: `locT_0003_percentile-ROI-lev4b7cdb1c61ede34200a74effa2c31c98.nii`

- **Pop-level parcel map**:  
  `LH_allParcels_language_noAngG.nii`

## Output Files Example

| Directory | Description |
|----------|-------------|
| `SyntCat/temp_data/data_all_runs/` | Raw `con_XXXX.nii` contrast files copied from subjects |
| `SyntCat/temp_data/clean_data_all_runs/` | Processed `.npy` files containing masked voxels from language fROIs |
| `froi_map.npy` | Numpy array mapping each extracted voxel to its fROI ID |

---

# `assemble_matrix.py`

This script constructs subject-level voxel-by-contrast matrices from previously masked `.npy` files. Each subject's `.npy` contrast files are stacked to form a 2D matrix (voxels × contrasts), which is then saved for downstream analyses.

---



