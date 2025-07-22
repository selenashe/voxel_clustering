# Created by Selena <jshe@mit.edu>

import os
import pandas as pd
import shutil
import numpy as np
import nibabel as nib

EXPT_NAME = 'SyntCat'
LOC_NAME = 'langlocSN'

subjects_df = pd.read_csv(f'/nese/mit/group/evlab/u/jshe/clustering/subjects/subjects_{EXPT_NAME}.csv')
analysis_path = '/nese/mit/group/evlab/u/jshe/clustering'
subjects_path = '/mindhive/evlab/u/Shared/SUBJECTS'
firstlevel_path = f'firstlevel_{EXPT_NAME}'
contrast_ids = ['0001', '0002', '0003', '0004', '0005', '0006', '0007', '0008',
                '0009', '0010', '0011', '0012', '0013', '0014', '0015', '0016', '0017', '0018']

data_path = f'{EXPT_NAME}/temp_data/data_all_runs'
clean_data_five_core_rois_path = f'{EXPT_NAME}/temp_data/clean_data_all_runs'

os.makedirs(data_path, exist_ok=True)
os.makedirs(clean_data_five_core_rois_path, exist_ok=True)

# individual langloc mask path
individual_lang_parcel_file = 'locT_0003_percentile-ROI-lev4b7cdb1c61ede34200a74effa2c31c98.nii'

def check_unique(matrix):
    # Flatten the matrix to 1D array
    flattened_matrix = matrix.flatten()

    # Get unique values and their counts
    unique_values, counts = np.unique(flattened_matrix, return_counts=True)

    # Print the unique values and their counts
    for value, count in zip(unique_values, counts):
        print(f"Value: {value}, Count: {count}")


def move_contrast_files():
    '''
    Moving the relevant spmT contrast files to the data folder
    '''
    for i in range(len(subjects_df)):
        subj_id = subjects_df[EXPT_NAME][i]

        contrast_file_path = os.path.join(subjects_path, subj_id, firstlevel_path)
        print(contrast_file_path)

        for idx in contrast_ids:
            print(idx) 
            filename = f'con_{idx}.nii'
            contrast_file = os.path.join(contrast_file_path, filename)
            
            dest_path = os.path.join(analysis_path, data_path, subj_id)
            
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

            shutil.copyfile(contrast_file, f'{dest_path}/{filename}')


def extract_lang_voxels(contrast_file, subj_loc_id):
    '''
    extract only lang-parcel-masked voxels for each contrast file
    '''
    
    # load individual lang locT file
    lang_loc_file = f'{subjects_path}/{subj_loc_id}/firstlevel_{LOC_NAME}/{individual_lang_parcel_file}' 
    lang_parcel_img = nib.load(lang_loc_file)
    lang_parcel_array = np.array(lang_parcel_img.dataobj)

    # load contrast files
    contrast_img = nib.load(contrast_file)
    contrast_array = np.array(contrast_img.dataobj)

    # making sure if lang parcel has binary entries
    check_unique(lang_parcel_array)

    # overlay lang parcel mask onto contrast files, get filtered array
    filtered_contrast_array = contrast_array[lang_parcel_array==1]    

    # get index to froi id mapping
    froi_indices = get_froi_index(lang_parcel_array)

    assert filtered_contrast_array.shape == froi_indices.shape
    
    return filtered_contrast_array, froi_indices


def get_froi_index(binary_top_10_parcel):
    '''Get an index mapping from every entry of the matrix to their froi labels'''
    reference_numerical_parcel_path = '/nese/mit/group/evlab/u/jshe/utils/parcels_and_atlas/LH_allParcels_language_noAngG.nii'
    
    # Load reference file and langloctop10 file
    reference_numerical_parcel = np.array(nib.load(reference_numerical_parcel_path).get_fdata())

    # Find indices where binary_top_10_parcel_path is 1
    indices = np.argwhere(binary_top_10_parcel == 1)

    # Get the corresponding values in reference_numerical_parcel_path at these indices
    froi_indices = reference_numerical_parcel[indices[:, 0], indices[:, 1], indices[:, 2]]

    return froi_indices

    
def keep_all_voxels(contrast_file):
    '''
    keep all voxels, not just lang
    '''
    contrast_img = nib.load(contrast_file)
    contrast_array = np.array(contrast_img.dataobj)
    return contrast_array


def save_lang_voxels_contrast():
    '''
    run extract_lang_voxels() for all contrast files in data/
    and save as .npy files in clean_data/
    '''
    for i in range(len(subjects_df)):
        subj_id = subjects_df[EXPT_NAME][i]
        subj_loc_id = subjects_df[LOC_NAME][i]

        target_dir = os.path.join(data_path, subj_id)
        print(target_dir)
        for file in os.listdir(target_dir):
            print(file)

            # UNCOMMENT FOR LANG VOXELS ONLY
            processed_array, froi_indices = extract_lang_voxels(f'{target_dir}/{file}', subj_loc_id)
            
            #processed_array = keep_all_voxels(f'{target_dir}/{file}')
            print(processed_array.shape)
            
            # build save path
            dest_path = os.path.join(analysis_path, clean_data_five_core_rois_path, subj_id)
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
            filename = file.strip('.nii')
            np.save(f'{dest_path}/{filename}.npy', processed_array)
        np.save(f'{dest_path}/froi_map.npy', froi_indices)


move_contrast_files()
save_lang_voxels_contrast()

