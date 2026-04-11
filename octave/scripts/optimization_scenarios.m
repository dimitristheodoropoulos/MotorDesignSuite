% Multi-scenario efficiency / torque analysis
clear; clc;

scenarios = {"low_load", "medium_load", "high_load"};
results = [];

for i = 1:length(scenarios)
    load = i * 50; % Nm
    efficiency = 0.85 - 0.01*i + 0.02*rand(); % dummy
    torque_ripple = 0.05*i + 0.01*rand();
    losses = 100 + 20*i + 10*rand();
    results = [results; i, load, efficiency, torque_ripple, losses];
end

% Σώσε σε CSV
fid = fopen('results/csv/optimization.csv','w');
fprintf(fid,"Scenario,Load,EFF,TorqueRipple,Losses\n");
for i = 1:size(results,1)
  fprintf(fid,"%d,%.2f,%.3f,%.3f,%.2f\n", results(i,:));
end
fclose(fid);
