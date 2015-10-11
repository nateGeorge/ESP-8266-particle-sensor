-- tables of air quality regimes and their maximum values
regimes = {}
-- Dylos scale
regimes[1] = {{0, 25, 50, 100, 350, 1000},{"Excellent", "Very good", "Good", "Fair", "Poor", "Very Poor"}}
-- Nate G's scale -- based on cancer study
regimes[2] = {{0, 847, 1531, 2134, 3202, 5524, 9926}, {"Excellent", "Good", "Fair", "Poor", "Very Poor", "Risky",
"Dangerous"}}
-- EPA scale
regimes[3] = {{0, 4919, 12660, 21509, 34483, 39021, 41989},{"Good", "Moderate", "Partly Unhealthy", "Unhealthy", 
"Very Unhealthy", "Hazardous", "Very Hazardous"}}

useRegime = 1;