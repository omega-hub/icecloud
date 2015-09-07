#version 150 compatibility
#extension GL_ARB_gpu_shader5 : enable

varying vec3 var_WorldPos;
varying vec3 var_Attribs;
varying float var_Timestamp;

uniform float unif_Alpha;

uniform float unif_FieldMin;
uniform float unif_FieldMax;

// Weights for the 4 output color components
uniform float unif_W1; // Angle
uniform float unif_W2; // Range
uniform float unif_W3; // Depth
uniform float unif_W4; // Dive

uniform vec2 unif_Selection;
uniform vec4 unif_SelectionColor;

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
    gl_Position = gl_ModelViewMatrix * gl_Vertex;
	
	vec3 w = vec3(unif_W1, unif_W2, unif_W3);
	vec3 inputData = vec3(gl_Color.r, gl_Color.g, gl_Vertex.z); 
	//vec3 inputData = gl_Color.rgb; 
	
	float colorW = (dot(w, inputData) - unif_FieldMin) / (unif_FieldMax - unif_FieldMin);
	
	vec3 endColor = vec3(0.1, 0.1, 1.0);
	vec3 startColor = vec3(1.0, 0.1, 0.0);
	
    // Set point color based on attribute value and selection interval
    float vmin = unif_XBounds[0];
    float vmax = unif_XBounds[1];
    float data[6] = float[6](gl_Vertex.x, gl_Vertex.y, gl_Vertex.z, gl_Color.r, gl_Color.g, gl_Color.b);
    float value = (data[unif_XAxisId] - vmin) / (vmax - vmin);

    if(value >= unif_Selection[0] && value <= unif_Selection[1])
        gl_FrontColor = unif_SelectionColor;
    else
    {
        gl_FrontColor = vec4(1,1,1,0.1);
        //gl_Position = vec4(0,0,0,1);
    }
}
