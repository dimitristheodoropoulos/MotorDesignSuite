%% run_phase3_headless.m (headless με qt)

% Βασικός φάκελος project
if exist('/app/data', 'dir')
    project_root = '/app';
elseif exist('./data', 'dir')
    project_root = pwd;  
else
    error('Δεν βρέθηκε φάκελος data.');
end

% Διαδρομές CSV
soft_mesh_file = fullfile(project_root, 'data', 'soft_mesh.csv');
hard_mesh_file = fullfile(project_root, 'data', 'hard_mesh.csv');

% Έλεγχος ύπαρξης αρχείων
if ~exist(soft_mesh_file, 'file')
    error('Δεν βρέθηκε το αρχείο: %s', soft_mesh_file);
end
if ~exist(hard_mesh_file, 'file')
    error('Δεν βρέθηκε το αρχείο: %s', hard_mesh_file);
end

%% Φόρτωση δεδομένων
soft_mesh = dlmread(soft_mesh_file);
hard_mesh = dlmread(hard_mesh_file);
fprintf('✅ Mesh files loaded successfully.\n');

%% Ρύθμιση γραφικών headless με qt
graphics_toolkit('qt');             % χρήση qt
set(0, 'defaultfigurevisible', 'off');  % off για headless

%% Εδώ ξεκινούν οι υπολογισμοί Phase 3
fprintf('Running Phase 3 computations...\n');

% Demo output
fprintf('Soft mesh size: %dx%d\n', size(soft_mesh));
fprintf('Hard mesh size: %dx%d\n', size(hard_mesh));
