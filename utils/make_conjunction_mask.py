import numpy as np
import nibabel as nib
import pandas as pd
import os

data_source = 'mroi'
contrasts = [('JS-NW', 'W-NW'), ('W-NW', 'JS-NW'), ('S-W', 'JS-NW'), ('S-W', 'W-NW')]

AFFINE = np.array([
    [-2.,0.,0.,90.],
    [0.,2.,0.,-126.],
    [0.,0.,2., -72.],
    [0.,0.,0.,1.],
    ])

if data_source == 'mroi':
    contrast_path = '/nese/mit/group/evlab/u/jshe/lang-voxel-decomp/swjn_mroi/original_analyses/n22_langlocSN/'
    contrast_map = {'JS-NW':20, 'W-NW':15, 'S-W':11} #contrasts to numerings in mroi outputs

elif data_source == 'firstlevel':
    contrast_path = '/nese/mit/group/evlab/u/jshe/lang-voxel-decomp/clean_data'
    contrast_map = {'JS-NW':'0020', 'W-NW':'0015', 'S-W':'0011'} #contrasts to numerings in mroi outputs
subjects_df = pd.read_csv('subjects.csv')


def check_unique(matrix):
    # Flatten the matrix to 1D array
    flattened_matrix = matrix.flatten()

    # Get unique values and their counts
    unique_values, counts = np.unique(flattened_matrix, return_counts=True)

    # Print the unique values and their counts
    for value, count in zip(unique_values, counts):
        print(f"Value: {value}, Count: {count}")


for contrast_pair in contrasts:
    # contrast1: the effect shown; contrast2: the effect not shown
    contrast_1, contrast_2 = contrast_pair
    print(contrast_1, contrast_2)

    id_1 = contrast_map[contrast_1]
    id_2 = contrast_map[contrast_2]

    print(id_1, id_2)
    
    if data_source == 'mroi':
        contrast_1_array = np.array(nib.load(f'{contrast_path}/spm_ss_mROI_T_00{id_1}.hdr').dataobj)
        contrast_2_array = np.array(nib.load(f'{contrast_path}/spm_ss_mROI_T_00{id_2}.hdr').dataobj)
        save_folder = 'mroi_conjunction_masks'
    
        contrast_1_array = np.where(contrast_1_array>0, 1, contrast_1_array)
        contrast_1_array = np.where(contrast_1_array<0, 0, contrast_1_array)

        contrast_2_array = np.where(contrast_2_array>0, 0, contrast_2_array)
        contrast_2_array = np.where(contrast_2_array<0, 1, contrast_2_array)
        
        contrast_1_mask = np.nan_to_num(contrast_1_array).astype(int)
        contrast_2_mask = np.nan_to_num(contrast_2_array).astype(int)
        
        print('checking for unique numbers (should only be 0 and 1)')
        check_unique(contrast_1_mask)
        check_unique(contrast_2_mask)

        conjunction_mask = np.multiply(contrast_1_mask, contrast_2_mask)
        conjunction_img = nib.Nifti1Image(conjunction_mask.astype(np.int16), affine=AFFINE)

        nib.save(conjunction_img, f'{save_folder}/{contrast_1}_not_{contrast_2}.nii')

    elif data_source == 'firstlevel':
        save_folder = 'firstlevel_conjunction_masks'
        
        for i in range(len(subjects_df)):
            subj = subjects_df['UID'][i]
            
            contrast_1_array = np.load(f'{contrast_path}/{subj}/spmT_{id_1}.npy')
            contrast_2_array = np.load(f'{contrast_path}/{subj}/spmT_{id_2}.npy')
 
            contrast_1_array = np.where(contrast_1_array>0, 1, contrast_1_array)
            contrast_1_array = np.where(contrast_1_array<0, 0, contrast_1_array)

            contrast_2_array = np.where(contrast_2_array>0, 0, contrast_2_array)
            contrast_2_array = np.where(contrast_2_array<0, 1, contrast_2_array)
            
            contrast_1_mask = np.nan_to_num(contrast_1_array).astype(int)
            contrast_2_mask = np.nan_to_num(contrast_2_array).astype(int)
            
            print('checking for unique numbers (should only be 0 and 1)')
            check_unique(contrast_1_mask)
            check_unique(contrast_2_mask)

            conjunction_mask = np.multiply(contrast_1_mask, contrast_2_mask)
            conjunction_img = nib.Nifti1Image(conjunction_mask.astype(np.int16), affine=AFFINE)
            
            dest_path = f'firstlevel_conjunction_masks/{subj}'
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

            nib.save(conjunction_img, f'{dest_path}/{contrast_1}_not_{contrast_2}.nii')




