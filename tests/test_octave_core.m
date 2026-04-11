% test_octave_core.m
printf("=== Testing Octave core scripts ===\n");

project_root = fileparts(fileparts(mfilename('fullpath')));
common_csv   = fullfile(project_root, 'python', 'scripts', 'phase3', ...
                        'common_inputs', 'csv');
results_csv  = fullfile(project_root, 'results', 'csv');

% Test 1: mesh CSV files
soft_csv = fullfile(common_csv, 'soft_mesh.csv');
hard_csv = fullfile(common_csv, 'hard_mesh.csv');

if exist(soft_csv, 'file') && exist(hard_csv, 'file')
    soft_data = csvread(soft_csv, 1, 0);
    hard_data = csvread(hard_csv, 1, 0);
    printf("✅ Mesh CSV files found.\n");
    printf("   Soft mesh nodes: %d\n", size(soft_data, 1));
    printf("   Hard mesh nodes: %d\n", size(hard_data, 1));
else
    printf("⚠️  Mesh CSV files missing at: %s\n", common_csv);
end

% Test 2: fea_results.csv
fea_results = fullfile(common_csv, 'fea_results.csv');
if exist(fea_results, 'file')
    data = csvread(fea_results, 1, 0);
    printf("✅ fea_results.csv found (%d rows)\n", size(data,1));
else
    printf("⚠️  fea_results.csv missing\n");
end

% Test 3: thermal_map.csv
thermal_csv = fullfile(results_csv, 'thermal_map.csv');
if exist(thermal_csv, 'file')
    tdata = csvread(thermal_csv);
    printf("✅ thermal_map.csv found (%d points)\n", size(tdata,1));
else
    printf("⚠️  thermal_map.csv missing\n");
end

% Test 4: vehicle_dynamics.csv
vd_csv = fullfile(results_csv, 'vehicle_dynamics.csv');
if exist(vd_csv, 'file')
    vdata = csvread(vd_csv);
    printf("✅ vehicle_dynamics.csv found (%d timesteps)\n", size(vdata,1));
else
    printf("⚠️  vehicle_dynamics.csv missing\n");
end

printf("\n=== Octave tests complete ===\n");