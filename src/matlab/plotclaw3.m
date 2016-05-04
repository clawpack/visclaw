%
% PLOTCLAW3 is the main driver routine for plotting 3d graphs for Clawpack.
%
%    PLOTCLAW3 is the main routine that the user calls to step through a
%    series of frames (i.e. fort.tXXXX and fort.qXXXX files).
%
%    Various parameters can be set in SETPLOT3.  The default version in
%    claw/matlab/setplot3.m can be copied to your directory and modifed to
%    set things up differently, or type 'k' at the prompt to get keyboard
%    control and change a value.
%
%    See also SETPLOT, PLOTFRAME3.

% generic plotting routine for clawpack and amrclaw output in matlab
% R. J. LeVeque, 1999
% Donna Calhoun, 2002
%
% Various parameters are set in setplot3.m
% The default version in claw/matlab/setplot3.m can be copied to your
% directory and modified to set things up differently, or type 'k'
% at the prompt to get keyboard control and change a value.
%
%---------------------------------------------------------------------

clawdim = 3;

disp(' ')
disp('plotclaw3  plots 3d results from clawpack or amrclaw')

set_value('NoQuery','NoQuery',0);

% set plotting parameters:
whichfile = which('setplot3');
if strcmp(whichfile,'')
    disp('*** No setplot3 file found')
else
    if (NoQuery == 0)
        inp = input(['Execute setplot3 (default = yes)? '],'s');
        if (isempty(inp))
            inp = 'y';
        end
    else
        inp = 'y';
    end;
    inpd = findstr('y',lower(inp));
    if (inpd == 1)
        setplot3;
        disp(['Executing m-script ' whichfile])
        disp(' ')
    end
end
disp(' ')

% the file setprob.m can be used to set up any necessary physical parameters
% or desired values of plotting parameters for this particular problem.

whichfile = which('setprob');
if strcmp(whichfile,'')
    %disp('*** No setprob file found')
  else
    disp(['Executing m-script ' whichfile])
    disp(' ')
    setprob
  end

%=============================================
% MAIN LOOP ON FRAMES:
%=============================================

if ~exist('MaxFrames')
  disp('MaxFrames parameter not set... you may need to execute setplot3')
  return
end

set_value('frameinc','plot_interval',1);
set_value('outputdir','OutputDir','./');
set_value('outputflag','OutputFlag','ascii');
set_value('outputprefix','plot_prefix','pltstate');
set_value('readblocknumber','ReadBlockNumber',0);

clear amrdata;
Frame = -frameinc;  % initialize frame counter
while Frame <= MaxFrames

  % pause for input from user to determine if we go to next frame,
  % look at data, or skip around.  This may reset Frame counter.

  old_Frame = Frame;
  queryframe  % this changes value of Frame

  if (old_Frame ~= Frame | isempty(amrdata))
    [amrdata,t] = readamrdata(clawdim,Frame,outputdir,outputflag,...
	outputprefix,readblocknumber);
  end;

  plotframe3;

end % main loop on frames
