@vertexShader

uniform vec2 unif_TextureTiling;
varying vec2 var_TexCoord;

varying float depth;

///////////////////////////////////////////////////////////////////////////////////////////////////
void setupSurfaceData(vec4 eyeSpacePosition)
{
    var_TexCoord = gl_MultiTexCoord0.xy * unif_TextureTiling;
    depth = gl_Vertex.z;
}