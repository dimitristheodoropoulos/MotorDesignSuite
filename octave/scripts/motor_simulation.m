% Motor Simulation - FEA mesh placeholder
project_root  = fileparts(fileparts(fileparts(mfilename('fullpath'))));
mesh_dir      = fullfile(project_root, 'python', 'scripts', 'phase3', ...
                         'common_inputs', 'csv');
soft_mesh_csv = fullfile(mesh_dir, 'soft_mesh.csv');
hard_mesh_csv = fullfile(mesh_dir, 'hard_mesh.csv');

if ~exist(soft_mesh_csv, 'file')
    warning('Soft mesh CSV not found: %s', soft_mesh_csv);
else
    printf('✅ Soft mesh found: %s\n', soft_mesh_csv);
end

if ~exist(hard_mesh_csv, 'file')
    warning('Hard mesh CSV not found: %s', hard_mesh_csv);
else
    printf('✅ Hard mesh found: %s\n', hard_mesh_csv);
end

printf('Would run FEA on %s\n', soft_mesh_csv);
printf('Would run FEA on %s\n', hard_mesh_csv);