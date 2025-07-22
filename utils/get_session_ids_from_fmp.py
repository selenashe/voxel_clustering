import numpy as np
import pandas as pd
import os

EXPT_NAME = 'SyntCat'
SUBJECTS_INFO = '/nese/mit/group/evlab/u/jshe/clustering/subjects'

subjects_dir = '/mindhive/evlab/u/Shared/SUBJECTS'
subjects_df = pd.read_csv('/nese/mit/group/evlab/u/jshe/clustering/subjects/subjects_fmp.csv')
experiment_df = subjects_df[subjects_df['Experiment'] == EXPT_NAME]

subject_list = []
for _, row in experiment_df.iterrows():
    subject_list.append(f"{int(row['Subjects::UniqueID'])}_{row['ScanSessions::SessionID']}_PL2017")

# check whether dir exists in SUBJECTS
for path in subject_list:
    if os.path.isdir(f"{subjects_dir}/{path}"):
        continue
    else:
        print(f"{subjects_dir}/{path} is NOT a directory")

# OPTIONAL: check whether that dir contains langloc
for d in subject_list:
    subdir_path = os.path.join(f'{subjects_dir}/{d}', 'firstlevel_langlocSN')
    if os.path.isdir(subdir_path):
        continue
    else:
        print(f"{subdir_path} does NOT exist.")


print('Subject count: ', len(subject_list))

# assumes langlocSN exists in the expt dir, need to manually replace the ones that don't have langloc
df = pd.DataFrame({EXPT_NAME: subject_list, 'langlocSN':subject_list})
df.to_csv(f'{SUBJECTS_INFO}/subjects_{EXPT_NAME}_temp.csv', index=False)