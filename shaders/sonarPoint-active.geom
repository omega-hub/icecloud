#version 150 compatibility
#extension GL_EXT_geometry_shader4: enable
#extension GL_ARB_gpu_shader5 : enable

uniform float pointScale;

uniform vec3 unif_TileX;
uniform vec3 unif_TileY;

flat out vec3 vertex_light_position;
flat out vec4 eye_position;
flat out float sphere_radius;

varying in vec3 var_WorldPos[];

// data point attributes
varying in float var_Timestamp[];
varying in vec3 var_Attribs[];

void
main(void)
{
    vec3 worldPos = var_WorldPos[0];
    
    //if(var_Timestamp[0] >= unif_SectionBounds[i][0] &&
    //    var_Timestamp[0] < unif_SectionBounds[i][1])
    {
        sphere_radius =  pointScale * 2.0;
        float halfsize = sphere_radius * 0.5;
        
        //if(unif_SectionFlags[i] == 0)
        //    gl_FrontColor = gl_FrontColorIn[0];
        //else
        gl_FrontColor = vec4(0.5,0.5,0,1);

        eye_position = gl_PositionIn[0];
        vertex_light_position = normalize(gl_LightSource[0].position.xyz - eye_position.xyz);

        gl_TexCoord[0].st = vec2(1.0,-1.0);
        gl_Position = gl_PositionIn[0];
        gl_Position.xy += vec2(halfsize, -halfsize);
        gl_Position = gl_ProjectionMatrix * gl_Position;
        EmitVertex();

        gl_TexCoord[0].st = vec2(1.0,1.0);
        gl_Position = gl_PositionIn[0];
        gl_Position.xy += vec2(halfsize, halfsize);
        gl_Position = gl_ProjectionMatrix * gl_Position;
        EmitVertex();

        gl_TexCoord[0].st = vec2(-1.0,-1.0);
        gl_Position = gl_PositionIn[0];
        gl_Position.xy += vec2(-halfsize, -halfsize);
        gl_Position = gl_ProjectionMatrix * gl_Position;
        EmitVertex();

        gl_TexCoord[0].st = vec2(-1.0,1.0);
        gl_Position = gl_PositionIn[0];
        gl_Position.xy += vec2(-halfsize, halfsize);
        gl_Position = gl_ProjectionMatrix * gl_Position;
        EmitVertex();

        EndPrimitive();
    }
}
