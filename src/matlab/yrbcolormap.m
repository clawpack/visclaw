function cmout = yrbcolormap(N)
%YRBCOLORMAP returns a yellow-red-blue colormap
% 
% YRBCOLORMAP sets the color map to a gradient of contrasting colors 
% going from yellow to red to blue.  
%
% YRBCOLORMAP(N) sets  a length N color map. The default is N=10.
%
% CM=YRBCOLORMAP(...) returns the colormap, but does not set it.

if (nargin == 0)
    N = 10;
end

c01 = linspace(0,1,N+1);
c10 = fliplr(c01);
% c10 = 1:-.1:0;
c0 = zeros(size(c01));
c1 = 1 + c0;
yrb = [c1' c10' c0'; c10' c0' c01'];
if (nargout > 0)
    cmout = yrb;
else
    colormap(yrb);
end

end

