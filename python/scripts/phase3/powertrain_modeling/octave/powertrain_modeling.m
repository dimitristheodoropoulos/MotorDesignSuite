% ============================================================================
% powertrain_modeling.m – Octave Phase3 headless (corrected)
% ============================================================================
pkg load io        % CSV reading/writing
pkg load statistics % optional

% Use gnuplot as graphics toolkit (headless)
graphics_toolkit('gnuplot');
set(0, 'defaultfigurevisible', 'off');  % ensure all figures are headless

% Directories (match docker-compose.override.yml)
results_dir = "../../phase3_results";
csv_dir     = [results_dir "/csv"];
plots_dir   = [results_dir "/plots"];

% Create directories if not existing
if ~exist(csv_dir, "dir")
    mkdir(csv_dir);
end
if ~exist(plots_dir, "dir")
    mkdir(plots_dir);
end

% -------------------------------
% 1️⃣ Load FEM results from FreeFEM
% -------------------------------
fea_csv = "../../common_inputs/csv/fea_results.csv";
if exist(fea_csv, "file")
    data = csvread(fea_csv, 1, 0); % skip header
    MeanCoreLoss = data(:,2);      % example: MeanCoreLoss column
    MaterialIndex = data(:,1);     % example: Material column (soft=1, hard=2)
else
    warning("FEA results CSV not found, using dummy values");
    MeanCoreLoss = [1;2];
    MaterialIndex = [1;2];
end

% -------------------------------
% 2️⃣ Dummy EM + thermal + mechanical calculations
% -------------------------------
Efficiency = 0.9 - 0.1*MeanCoreLoss/max(MeanCoreLoss);
Torque     = 10 + 5*MeanCoreLoss/max(MeanCoreLoss);
Heat       = 40*MeanCoreLoss/max(MeanCoreLoss);

% Multi-criteria score
Score = Efficiency ./ (Heat + 1e-6);

% -------------------------------
% 3️⃣ Save results CSV
% -------------------------------
output_csv = [csv_dir "/powertrain_octave_results.csv"];
csvwrite(output_csv, [Efficiency Torque Heat Score]);
disp(["✅ Octave results saved to: " output_csv]);

% -------------------------------
% 4️⃣ Generate plots (headless)
% -------------------------------
% Core Loss Bar
h1 = figure;
bar(MeanCoreLoss);
title('Core Loss Map'); 
xlabel('Material Node'); 
ylabel('Core Loss [W/kg]');
print(h1, [plots_dir "/core_loss_octave.png"], "-dpng");
close(h1);

% Torque Bar
h2 = figure;
bar(Torque);
title('Torque Map');
xlabel('Material Node');
ylabel('Torque [Nm]');
print(h2, [plots_dir "/torque_octave.png"], "-dpng");
close(h2);

disp("✅ Octave plots saved in phase3_results/plots");
