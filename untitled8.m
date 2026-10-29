% =========================================================================
% Project: Community Flood Emergency Map (Cabuyao, Laguna)
% Script: MATLAB Backend Data Processor
% Description: Processes community flood reports, matches them with local 
%              evacuation centers, and exports tables for Streamlit.
% =========================================================================

clear; clc;

disp('Processing Cabuyao, Laguna flood and evacuation data...');

% -------------------------------------------------------------------------
% 1. Define Evacuation Centers in Cabuyao, Laguna
% -------------------------------------------------------------------------
evac_names = {
    'Cabuyao City Gymnasium', ...
    'Pulo Elementary School', ...
    'Marinig Gymnasium', ...
    'Banlic Elementary School', ...
    'Sala Barangay Hall & Covered Court'
    };

% Approximate latitude and longitude coordinates in Cabuyao, Laguna
evac_lat = [14.2778, 14.2650, 14.3012, 14.2589, 14.2720];
evac_lon = [121.1214, 121.1320, 121.1450, 121.1150, 121.1280];
evac_capacity = [500, 300, 400, 250, 200];
evac_current_load = [120, 250, 80, 50, 90];

evac_table = table(evac_names', evac_lat', evac_lon', evac_capacity', evac_current_load', ...
    'VariableNames', {'FacilityName', 'Latitude', 'Longitude', 'Capacity', 'CurrentLoad'});

% -------------------------------------------------------------------------
% 2. Simulate/Process Live Community Flood Reports
% -------------------------------------------------------------------------
report_id = [101, 102, 103, 104, 105];
barangays = {'Marinig', 'Banlic', 'Pulo', 'Sala', 'Diezmo'};
report_lat = [14.2980, 14.2600, 14.2640, 14.2750, 14.2850];
report_lon = [121.1420, 121.1180, 121.1300, 121.1250, 121.1350];
water_level_cm = [85, 30, 120, 45, 10]; 
status_labels = {'Critical', 'Low', 'Critical', 'Moderate', 'Safe'};

flood_table = table(report_id', barangays', report_lat', report_lon', water_level_cm', status_labels', ...
    'VariableNames', {'ReportID', 'Barangay', 'Latitude', 'Longitude', 'WaterLevel_cm', 'Severity'});

% -------------------------------------------------------------------------
% 3. Spatial Analysis: Match Flood Reports to Nearest Evacuation Center
% -------------------------------------------------------------------------
nearest_evac = cell(height(flood_table), 1);
min_distance_km = zeros(height(flood_table), 1);

for i = 1:height(flood_table)
    dists = zeros(height(evac_table), 1);
    for j = 1:height(evac_table)
        % Haversine/Euclidean approximation for local distances (1 deg ~ 111 km)
        dists(j) = sqrt((flood_table.Latitude(i) - evac_table.Latitude(j))^2 + ...
            (flood_table.Longitude(i) - evac_table.Longitude(j))^2) * 111;
    end
    [min_d, idx] = min(dists);
    min_distance_km(i) = round(min_d, 2);
    nearest_evac{i} = evac_table.FacilityName{idx};
end

flood_table.NearestEvacuationCenter = nearest_evac;
flood_table.DistanceToEvac_km = min_distance_km;

% -------------------------------------------------------------------------
% 4. Export Clean Datasets for Streamlit Frontend
% -------------------------------------------------------------------------
writetable(flood_table, 'processed_flood_reports.csv');
writetable(evac_table, 'evacuation_centers.csv');

disp('Success! Files "processed_flood_reports.csv" and "evacuation_centers.csv" generated.');