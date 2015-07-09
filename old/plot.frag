#version 150 compatibility
#extension GL_ARB_gpu_shader5 : enable

void main (void)
{
    float x = gl_TexCoord[0].x;
    float y = gl_TexCoord[0].y;
    float zz = 1.0 - x*x - y*y;

    if (zz <= 0.0 )
    	discard;

    gl_FragColor = gl_Color;
}
