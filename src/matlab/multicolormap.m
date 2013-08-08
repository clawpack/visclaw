function cm = multicolormap(n,s)

% MULTICOLORMAP returns a colormap of distinct colors
%
% CM = MULTICOLORMAP(N) creates a colormap of N colors which should be fairly
% distinct an can be used to color regions of a map.
%
% MULTICOLOR(N,S) takes a random seed which the user can set to obtain
% a fixed colormap.
%

if (nargin > 1)
  rand('state',s);
end;

N1 = 4;
N2 = 4;
N3 = 4;
npmax = N1*N2*N3;
k = 1;
N = 3;
for ii = 1:N1,
  xlow = (ii-1)/N1;
  for jj = 1:N2,
    ylow = (jj-1)/N2;
    for kk = 1:N3,
      zlow = (kk-1)/N3;
      cm(k,:) = [xlow ylow zlow] + 0.5./[N1 N2 N3];
      k = k + 1;
    end;
  end;
end;
[r,idx] = sort(rand(npmax,1));

cm = cm(idx(1:n),:);
