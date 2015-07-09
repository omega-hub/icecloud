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


void main(void)
{
    //gl_FrontColor = gl_Color;

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
	
	gl_FrontColor.rgb = mix(startColor, endColor, colorW);
	gl_FrontColor.rgb = mix(gl_FrontColor.rgb, gl_FrontMaterial.diffuse.rgb, unif_W4);
    gl_FrontColor.a = unif_Alpha;
}
