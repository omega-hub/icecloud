@surfaceShader

uniform float unif_Shininess;
uniform float unif_Gloss;

varying vec3 var_Normal;
varying float depth;

///////////////////////////////////////////////////////////////////////////////////////////////////
SurfaceData getSurfaceData(void)
{
    SurfaceData sd;
    sd.albedo = gl_FrontMaterial.diffuse; 
    sd.emissive.rgb = gl_FrontMaterial.emission.rgb * step(0.98, sin(depth * 4));
    sd.emissive.a = 1.0;
    sd.shininess = 0;
    sd.gloss = 0;
    sd.normal = normalize(var_Normal);
    
    return sd;
}
