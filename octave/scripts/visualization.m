% Octave Visualization – MotorDesignSuite
project_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
mesh_dir     = fullfile(project_root, 'python', 'scripts', 'phase3', ...
                        'common_inputs', 'csv');
plots_dir    = fullfile(project_root, 'results', 'plots');

if ~exist(plots_dir, 'dir'); mkdir(plots_dir); end

soft_csv = fullfile(mesh_dir, 'soft_mesh.csv');
hard_csv = fullfile(mesh_dir, 'hard_mesh.csv');

if ~exist(soft_csv, 'file')
    warning('Soft mesh CSV not found: %s', soft_csv); return;
end
if ~exist(hard_csv, 'file')
    warning('Hard mesh CSV not found: %s', hard_csv); return;
end

printf('Generating plots for %s and %s...\n', soft_csv, hard_csv);

soft_mesh = csvread(soft_csv, 1, 0);
hard_mesh = csvread(hard_csv, 1, 0);

% --- Graphics toolkit (headless) ---
try
    graphics_toolkit('qt');
catch
    graphics_toolkit('gnuplot');
end
set(0, 'DefaultFigureVisible', 'off');
set(0, 'DefaultAxesFontName',  'DejaVu Sans');
set(0, 'DefaultTextFontName',  'DejaVu Sans');

% --- Soft mesh plot ---
figure;
plot(soft_mesh(:,1), soft_mesh(:,2), 'bo');
title('Soft Magnetic Mesh Nodes');
xlabel('X'); ylabel('Y'); grid on;
print('-dpng', fullfile(plots_dir, 'soft_mesh.png'));

% --- Hard mesh plot ---
figure;
plot(hard_mesh(:,1), hard_mesh(:,2), 'ro');
title('Hard Magnetic Mesh Nodes');
xlabel('X'); ylabel('Y'); grid on;
print('-dpng', fullfile(plots_dir, 'hard_mesh.png'));

printf('✅ Plots saved to %s\n', plots_dir);