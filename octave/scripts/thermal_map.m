% Simple thermal model
project_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
csv_dir      = fullfile(project_root, 'results', 'csv');
plots_dir    = fullfile(project_root, 'results', 'plots');

if ~exist(csv_dir,   'dir'); mkdir(csv_dir);   end
if ~exist(plots_dir, 'dir'); mkdir(plots_dir); end

losses             = linspace(100, 500, 10);
ambient            = 25;
thermal_resistance = 0.1;  % K/W
temperature        = ambient + losses * thermal_resistance;

csvwrite(fullfile(csv_dir, 'thermal_map.csv'), [losses' temperature']);

figure('Visible', 'off');
plot(losses, temperature, 'm-o', 'LineWidth', 2);
xlabel('Losses [W]'); ylabel('Temperature [C]');
title('Thermal Map'); grid on;
print('-dpng', fullfile(plots_dir, 'thermal_map.png'));

printf('✅ thermal_map.csv and thermal_map.png saved\n');