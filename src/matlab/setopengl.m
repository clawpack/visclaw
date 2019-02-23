function has_opengl = setopengl()

% SETOPENGL sets the graphics renderer to OpenGL.
%
%    SETOPENGL sets the current graphics renderer to OpenGL, if this
%    renderer is available on your system, and returns a warning otherwise.
%
%    Many 3d graphics features are rendered much better using OpenGL, so
%    it is suggested that it be used whenever possible.
%
%    SETOPENGL sets the 'Renderer' property of the current figure to
%    'opengl'.
%
%    HAS_OPENGL = SETOPENGL() returns TRUE if the system has OpenGL and 
%    FALSE otherwise;
%
%    Some graphics hardware may not support the OpenGL renderer, or may
%    cause certain Matlab routines to crash. For this reason, the choice
%    of whether to use OpenGL is left to the user.
%
%    See also OPENGL, FIGURE, GCF.

rset = set(gcf,'Renderer');
found_opengl = 0;
for i = 1:length(rset)
  if (strcmp(lower(rset(i)),'opengl'))
    found_opengl = 1;
  end
end

if (~found_opengl)
    disp('*** Warning : The OpenGL renderer is not available on your system.');
else
    if (nargout == 0)
        set(gcf,'Renderer','opengl');
    else
        has_opengl = found_opengl;
    end
end
