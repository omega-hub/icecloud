#version 150 compatibility
#extension GL_ARB_gpu_shader5 : enable

varying vec3 var_WorldPos;
varying vec3 var_Attribs;
varying float var_Timestamp;

uniform float unif_Alpha;

uniform vec2 unif_XBounds;
uniform vec2 unif_YBounds;
uniform int unif_XAxisId;
uniform int unif_YAxisId;

void main(void)
{
	// Color field contains point attributes.
	var_Attribs = gl_Color.rgb;
    var_Timestamp = gl_Color.b;
    var_Attribs.b = gl_Vertex.z;
	
	var_WorldPos = gl_Vertex.xyz;
    // return projection position
    //gl_Position = gl_ModelViewMatrix * gl_Vertex;
    
    float xmin = unif_XBounds[0];
    float xmax = unif_XBounds[1];

    float ymin = unif_YBounds[0];
    float ymax = unif_YBounds[1];
    
    float data[6] = float[6](gl_Vertex.x, gl_Vertex.y, gl_Vertex.z, gl_Color.r, gl_Color.g, gl_Color.b);
    
    gl_Position.x = ((data[unif_XAxisId] - xmin) / (xmax - xmin) - 0.5) * 2;
    gl_Position.y = ((data[unif_YAxisId] - ymin) / (ymax - ymin) - 0.5) * -2;
    gl_Position.z = 1;
    gl_Position.w = 1;
    
    gl_FrontColor = vec4(1,1,1,0.2);
}
