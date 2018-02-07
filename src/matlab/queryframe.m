%  QUERYFRAME used by PLOTCLAW1, PLOTCLAW2 and PLOTCLAW3 to loop through data.
%
%      QUERYFRAME is normally called directly from PLOWCLAW<N>, and so is
%      not typically called by the user.  However, the user can supress the
%      query option by setting the 'NoQuery' parameter to 1.  This is used
%      for example, in making movies.
%
%      See also PLOTCLAW1, PLOTCLAW2, PLOTCLAW3.

if exist('NoQuery')
    if NoQuery == 1
        % set NoQuery=1 if you want the plots to be produced with no
        % query in between.  Particularly useful if you want lots of frames to
        % be printed out for an animation (put a command like makeframegif
        % in afterframe.m and set NoQuery=1)
        pause(1)
        Frame = Frame + frameinc;
        if Frame > MaxFrames
            return  % break out of plotclawN after last frame
        end
        return
    end
end


query_quit = false;
inp = 'k';
while strcmp(inp,'k')
    
    if (clawdim < 3)
        inp = input(...
            ['Hit <return> for next plot, or type k, r, rr, j, i, q, or ?  '],'s');
    else
        inp = input(...
            ['Hit <return> for next plot, or type k, r, rr, j, i, x, y, z, q, or ?  '],'s');
    end
    
    if strcmp(inp,'?')
        disp('  k  -- keyboard input.  Type any commands and then "return"')
        disp('  r  -- redraw current frame, without re-reading data')
        disp('  rr -- re-read current file,and redraw frame');
        disp('  j  -- jump to a particular frame')
        disp('  i  -- info about parameters and solution')
        if (clawdim == 3)
            disp('  x  -- loop over slices in x direction (3d only)')
            disp('  y  -- loop over slices in y direction (3d only)')
            disp('  z  -- loop over slices in z direction (3d only)')
        end
        disp('  q  -- quit')
        inp = 'k';
    elseif strcmp(inp,'k')
        keyboard
    elseif strcmp(inp,'r')
        % redraw:  leave Frame counter alone
        if Frame == -frameinc
            disp('Cannot redraw yet')
            inp = 'k';
        end
    elseif strcmp(inp,'rr')
        if Frame == -frameinc
            disp('Cannot redraw yet')
            inp = 'k';
        end
        % redraw frame AND re-read data
        amrdata = [];
    elseif strcmp(inp,'x')
        if (clawdim < 3)
            continue
        end
        if Frame == -frameinc
            disp('Nothing to loop over yet!')
            inp = 'k';
        else
            % Loop over x slices
            sliceloop('x');
            % Continue with same frame.
            inp = 'k';
        end
    elseif strcmp(inp,'y')
        if (clawdim < 3)
            continue
        end
        if Frame == -frameinc
            disp('Nothing to loop over yet!')
            inp = 'k';
        else
            % Loop over x slices
            sliceloop('y');
            % Continue with same frame.
            inp = 'k';
        end
    elseif strcmp(inp,'z')
        if (clawdim < 3)
            continue
        end
        if Frame == -frameinc
            disp('Nothing to loop over yet!')
            inp = 'k';
        else
            % Loop over x slices
            sliceloop('z');
            % Continue with same frame.
            inp = 'k';
        end
    elseif strcmp(inp,'j')
        Frame = input('Frame to jump to? ');
    elseif strcmp(inp,'i')
        if clawdim == 1
            infoplot1
            disp(' ')
            disp(' ')
            disp('hit <return> for information about this frame')
            pause
            infoframe1
        end
        if clawdim == 2
            infoplot2
            disp(' ')
            disp('hit <return> for information about this frame')
            pause
            infoframe2
        end
        if clawdim == 3
            infoplot3
            disp(' ');
            disp('hit <return> for information about this frame');
            pause
            infoframe3
        end
        inp = 'k';
    elseif isempty(inp)
        % go to next frame
        Frame = Frame + frameinc;
    elseif (~strcmp(inp,'q'))
        % quit handled separately below.
        % Otherwise unrecognized input, go back and try again
        inp = 'k';
    end % if strcmp
end % while strcmp

if strcmp(inp,'q')
    query_quit = true;
    return  % Breaks from while loop in plotclaw2
end

if strcmp(inp,'k')
    enter_debug_mode = true;
    return
end


