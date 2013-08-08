function pressure = pressure(data)
%
% Compute the pressure from Euler data in N dimensions
% assumes data contains density in first column, energy in last column,
% and components of momentum in between.
%
% Assumes a gamma-law ideal gas.
% gamma = 1.4 is hardwired here, but you can change this or modify
% to read in the proper value from setprob.data, for example.
%
% This routine can be modified for a different equation of state,
% or if the data doesn't have the required format.

gamma = 1.4;
rho = data(:,1);
energy = data(:,end);
mom = data(:,2:end-1);
mom2 = mom .* mom;
kinetic = 0.5 * sum(mom2,2) ./ rho;
pressure = (gamma-1) * (energy - kinetic);
