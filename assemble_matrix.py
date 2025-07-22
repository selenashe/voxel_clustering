import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA, FastICA

EXPT = 'SyntCat'

# Directory containing the .npy files
data_directory = f'{EXPT}/temp_data/clean_data_all_runs'

# Directroy to output clean matrix
matrix_directory = f'{EXPT}/clean_matrix_all_runs'
os.makedirs(matrix_directory, exist_ok=True)

def assemble_matrix():
    for subj_folder in list(subdir[0] for subdir in os.walk(data_directory))[1:]:
        
        assert subj_folder.endswith('PL2017')

        # List all .npy files in the directory
        npy_files = [file for file in os.listdir(subj_folder) if file.endswith('.npy') and file.startswith('con')]
         
        # Sort the file names in ascending order
        npy_files.sort()

        print(npy_files)

        # Initialize an empty list to store the content of each .npy file
        file_content = []

        # Iterate through each .npy file
        for file_name in npy_files:
            # Load the content of the .npy file
            print(os.path.join(subj_folder, file_name))

            content = np.load(os.path.join(subj_folder, file_name), allow_pickle=True)
            # Append the content to the list
            file_content.append(content)

        # load froi index file
        froi_map = np.load(os.path.join(subj_folder, 'froi_map.npy'))

        # Turn list into matrix and transpose the matrix
        big_matrix = np.array(file_content)
        big_matrix = big_matrix.T
        
        # For all voxels
        big_matrix = big_matrix.reshape(-1, big_matrix.shape[-1])
        
        # Print the shape of the big matrix
        print("Shape of big matrix:", big_matrix.shape)
        print(subj_folder)
        save_filename = subj_folder.removeprefix(f'{EXPT}/temp_data/clean_data_all_runs/')

        print(save_filename)
        np.save(f'{matrix_directory}/{save_filename}.npy', big_matrix)
        np.save(f'{matrix_directory}/{save_filename}_froi_map.npy', froi_map)

assemble_matrix()
