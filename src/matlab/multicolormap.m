function cm = multicolormap(n,s)
%
% MULTICOLORMAP returns a colormap of distinct colors
%
% CM = MULTICOLORMAP(N) creates a colormap of N colors which should be fairly
% distinct and can be used to color regions of a map.
%
% MULTICOLOR(N,S) takes a random seed which the user can set to obtain
% a fixed colormap.
%

if (nargin > 1)
  rand('seed',s);
end;

% Grid in colorcube for obtaining distinct colors.
N1 = 5;
N2 = 5;
N3 = 5;
npmax = N1*N2*N3;

% rc = rand(npmax,1);   % Choose randomly in each sub-cube
rc = 0.25*ones(npmax,1); % Always choose color at center of cube

k = 1;
for ii = 1:N1,
  xlow = (ii-1)/N1;
  for jj = 1:N2,
    ylow = (jj-1)/N2;
    for kk = 1:N3,
      zlow = (kk-1)/N3;
      cm(k,:) = [xlow ylow zlow] + rc(k)./[N1 N2 N3];
      k = k + 1;
    end
  end
end

% Choose colors randomly from colors chosen for each subcube
[r,idx] = sort(rand(npmax,1));

% Index into grid of subcubes.
cm = cm(idx(1:n),:);
