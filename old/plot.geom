#version 150 compatibility
#extension GL_EXT_geometry_shader4: enable
#extension GL_ARB_gpu_shader5 : enable

uniform float pointScale;

// data point attributes
varying in float var_Timestamp[];
varying in vec3 var_Attribs[];

uniform int unif_NumSections;
uniform int unif_SectionFlags[16];
uniform vec2 unif_SectionBounds[16];
uniform vec3 unif_MaxAttrib[16];
uniform vec3 unif_MinAttrib[16];

void
main(void)
{
    gl_FrontColor = vec4(1,0,0,1);
    for(int i = 0; i < unif_NumSections; i++)
    {
        if(var_Timestamp[0] >= unif_SectionBounds[i][0] &&
            var_Timestamp[0] < unif_SectionBounds[i][1])
            {
                if(all(greaterThan(var_Attribs[0], unif_MinAttrib[i])) && 
                    all(lessThan(var_Attribs[0], unif_MaxAttrib[i])))
                {
                    if(unif_SectionFlags[i] == 0)
                        gl_FrontColor = gl_FrontColorIn[0];
                    else
                        gl_FrontColor = vec4(0,1,0,1);
                }
        }
    }
    
    float halfsize = pointScale;
    
    gl_TexCoord[0].st = vec2(1.0,-1.0);
    gl_Position = gl_PositionIn[0];
    gl_Position.xy += vec2(halfsize, -halfsize);
    EmitVertex();

    gl_TexCoord[0].st = vec2(1.0,1.0);
    gl_Position = gl_PositionIn[0];
    gl_Position.xy += vec2(halfsize, halfsize);
    EmitVertex();

    gl_TexCoord[0].st = vec2(-1.0,-1.0);
    gl_Position = gl_PositionIn[0];
    gl_Position.xy += vec2(-halfsize, -halfsize);
    EmitVertex();

    gl_TexCoord[0].st = vec2(-1.0,1.0);
    gl_Position = gl_PositionIn[0];
    gl_Position.xy += vec2(-halfsize, halfsize);
    EmitVertex();

    EndPrimitive();
}
