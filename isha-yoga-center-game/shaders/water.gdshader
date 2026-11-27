shader_type spatial;
render_mode blend_mix, depth_draw_always, cull_disabled;

uniform vec4 water_color : source_color = vec4(0.04, 0.20, 0.24, 0.55);
uniform vec4 deep_color : source_color = vec4(0.01, 0.07, 0.10, 0.88);
uniform float roughness : hint_range(0.0, 1.0) = 0.015;
uniform float metallic : hint_range(0.0, 1.0) = 0.05;
uniform sampler2D noise_tex : hint_normal;
uniform sampler2D DEPTH_TEXTURE : hint_depth_texture, filter_linear_mipmap;

void fragment() {
	// Dual scrolling wave ripples
	vec2 uv1 = UV * 4.0 + vec2(TIME * 0.02, TIME * 0.015);
	vec2 uv2 = UV * 6.5 - vec2(TIME * 0.016, -TIME * 0.022);
	vec3 n1 = texture(noise_tex, uv1).rgb;
	vec3 n2 = texture(noise_tex, uv2).rgb;
	NORMAL_MAP = mix(n1, n2, 0.5);
	NORMAL_MAP_DEPTH = 1.3;

	// Smooth physical depth absorption
	float depth = texture(DEPTH_TEXTURE, SCREEN_UV).r;
	vec4 upos = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, depth, 1.0);
	vec3 pixel_position = upos.xyz / upos.w;
	float diff = max(0.0, VERTEX.z - pixel_position.z);
	float depth_fade = 1.0 - exp(-diff * 2.5);

	// Gentle water-contact meniscus edge along stone walls and linga
	float edge = clamp(1.0 - diff * 25.0, 0.0, 1.0);
	edge = pow(edge, 4.0);

	// Realistic Fresnel reflection
	float fresnel = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 4.0);

	vec4 base_water = mix(water_color, deep_color, depth_fade);
	vec3 water_rgb = mix(base_water.rgb, vec3(0.70, 0.88, 0.98), fresnel * 0.40);
	water_rgb = mix(water_rgb, vec3(0.55, 0.75, 0.85), edge * 0.45);

	ALBEDO = water_rgb;
	ALPHA = mix(base_water.a, 0.92, fresnel);
	ROUGHNESS = roughness;
	METALLIC = metallic;
	SPECULAR = 0.98;
}
