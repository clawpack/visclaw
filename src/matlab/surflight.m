function h = surflight()
%SURFLIGHT illuminates surfaces without affecting slices.
%
%   SURFLIGHT() illuminates surfaces using CAMLIGHT, without
%   affecting the illumination on slices.  This prevents slices from
%   becomeing too dark.  This is accomplished by setting the 'facelighting'
%   property of each slice to 'none'.
% 
%   H = SURFLIGHT() returns a handle to the camera light.
% 
%   See also CAMLIGHT, LIGHT.
%


% Turn off ambient strength on all slices.
sdirs = {'x', 'y','z'};
for idir = 1:length(sdirs),
    slices = get_slices(sdirs{idir});
    snum = 1:length(slices);
    for ns = 1:length(snum),
        n = snum(ns);
        if (n < 1 | n > length(slices))
            continue;
        end
        slice = slices{n};
        level = 1:length(slice);        
        for l = 1:length(level),
            pvec = slice{level(l)};
            for k = 1:length(pvec),
                p = pvec(k);  % Patch on slice
                set(p,'facelighting','none');
            end
        end
    end
end

h = camlight;

