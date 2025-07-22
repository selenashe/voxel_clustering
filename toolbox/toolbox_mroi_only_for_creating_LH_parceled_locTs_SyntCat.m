addpath('/om/group/evlab/software/conn')
conn_module('el','init');

% defining contrasts and expt name
loc_task = 'langlocSN';
eoi_task = 'SyntCat';

localizer_contrasts = {'S-N'};
effectofinterest_contrasts = {'N_hi','N_hm','N_lm','N_lo','AJ_hi','AJ_hm','AJ_lm','AJ_lo','V_hi','V_hm','V_lm','V_lo','AV_hi','AV_hm','AV_lm','AV_lo','FW_hi','FW_lo'};
expt = 'for_creating_LH_locT_files_SyntCat';

% defining subject and output paths
subject_dir = '/mindhive/evlab/u/Shared/SUBJECTS/';
results_dir = ['/nese/mit/group/evlab/u/jshe/clustering/toolbox/results/' expt];
subject_csv = '/nese/mit/group/evlab/u/jshe/clustering/subjects/subjects_SyntCat.csv';

% lang parcel
parcel_file = '/nese/mit/group/evlab/u/jelizlee/parcels/LH_allParcels_language_noAngG.nii';

subjects_table = readtable(subject_csv, 'Delimiter', ',');
localizer_subject_paths = subjects_table.(loc_task);
effectofinterest_subject_paths = subjects_table.(eoi_task);

% defining localizer & effect of interest paths
localizer_dir = ['firstlevel_' loc_task];
effectofinterest_dir = ['firstlevel_' eoi_task];

% assembling spm file matrix
localizer_spmfiles={}; 
effectofinterest_spmfiles={};

for nsub=1:length(localizer_subject_paths)
    localizer_spmfiles{nsub}=fullfile(subject_dir,localizer_subject_paths{nsub},localizer_dir,'SPM.mat');
    effectofinterest_spmfiles{nsub}=fullfile(subject_dir,effectofinterest_subject_paths{nsub},effectofinterest_dir,'SPM.mat');
end %note: size is is num_contrasts x num_subjects


% toolbox stuff
ss=struct(...
    'swd',results_dir,...   % output directory
    'Localizer_spm',{localizer_spmfiles},...
    'Localizer_contrasts',{localizer_contrasts},...   
    'EffectOfInterest_spm',{effectofinterest_spmfiles},...
    'EffectOfInterest_contrasts',{effectofinterest_contrasts},...% localizer contrast 
    'Localizer_thr_type',{'percentile-ROI-level'},...  % appendix F, paper by Alfonso & Ev, 2012, has all the options
    'Localizer_thr_p',0.1,... % proportion, not actually significance level (what proportion of ROI will be used, IF localizer_thr_type is percentile-ROI-level
    'type','mROI',...  % can be 'GcSS', 'mROI', or 'voxel'
    'ManualROIs', parcel_file,...
    'overlap_thr_roi', 0,...    
    'model',1,...    % can be 1 (one-sample t-test), 2 (two-sample t-test), or 3 (multiple regression), usually 1
    'estimation','OLS',... % basically always use, ordinary least squares, as opposed to ReML
    'overwrite',true,... % clears stuff from earlier toolbox analyses
    'ExplicitMasking',[],...    
    'ask','none');    % can be 'none' (any missing information is assumed to take default values), 'missing' (any missing information will be asked to the user), 'all' (it will ask for confirmation on each parameter)
ss=spm_ss_design(ss);    % see help spm_ss_design for additional information
ss=spm_ss_estimate(ss);  % can be found in /software/spm_ss
