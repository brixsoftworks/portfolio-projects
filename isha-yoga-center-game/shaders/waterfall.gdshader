shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_disabled;

// Realistic Volumetric Cascading Sacred Waterfall Shader - Radiant emerald-turquoise mineral water matching the pool
uniform vec4 water_color : source_color = vec4(0.08, 0.58, 0.54, 0.95); // Luminous sacred turquoise matching pool
uniform vec4 foam_color : source_color = vec4(0.90, 0.98, 0.96, 0.95); // White-water aerated froth & mist
uniform sampler2D albedo_tex : source_color, filter_linear_mipmap, repeat_enable;
uniform sampler2D normal_tex : hint_normal, filter_linear_mipmap, repeat_enable;
uniform sampler2D roughness_tex : hint_default_white, filter_linear_mipmap, repeat_enable;

uniform float flow_speed : hint_range(0.0, 8.0) = 3.0;
uniform float secondary_speed : hint_range(0.0, 10.0) = 4.5;
uniform float normal_depth : hint_range(0.0, 3.0) = 1.75;
uniform float wave_amplitude : hint_range(0.0, 0.3) = 0.05;

void vertex() {
	float uz = UV.y;
	// Dynamic fluid wave ripple increasing with fall distance
	float wave1 = sin(TIME * 4.5 + VERTEX.x * 2.2 + uz * 8.0);
	float wave2 = cos(TIME * 6.2 - VERTEX.x * 3.4 + uz * 12.0);
	VERTEX.z += (wave1 * 0.6 + wave2 * 0.4) * wave_amplitude * smoothstep(0.02, 0.30, uz);
}

void fragment() {
	float uz = UV.y;
	// Ballistic gravitational acceleration: v(z) increases with sqrt(depth)
	float grav_accel = 1.0 + 1.85 * sqrt(clamp(uz, 0.0, 1.0));
	
	// Stream stretching & turbulence under gravity
	float x_turb = sin(TIME * 2.2 + uz * 6.0) * 0.02;
	vec2 uv_fast = vec2(UV.x * 1.5 + x_turb, UV.y * 3.2 - TIME * flow_speed * grav_accel);
	vec2 uv_slow = vec2(UV.x * 2.2 - x_turb * 1.2, UV.y * 5.0 - TIME * secondary_speed * grav_accel);

	vec4 tex_fast = texture(albedo_tex, uv_fast);
	vec4 tex_slow = texture(albedo_tex, uv_slow);
	vec4 flow_tex = mix(tex_fast, tex_slow, 0.50);

	vec3 n_fast = texture(normal_tex, uv_fast).rgb * 2.0 - 1.0;
	vec3 n_slow = texture(normal_tex, uv_slow).rgb * 2.0 - 1.0;
	vec3 mixed_normal = normalize(n_fast + n_slow * 0.70);
	NORMAL_MAP = mixed_normal * 0.5 + 0.5;
	NORMAL_MAP_DEPTH = normal_depth;

	// Cascading white-water rapids and turbulence
	// 1. Turbulent crest froth pouring over rock weir
	float crest_foam = smoothstep(0.09, 0.01, uz) * 0.70;
	// 2. Churning impact froth where water hits pool
	float impact_foam = smoothstep(0.82, 0.98, uz) * 0.85;
	// 3. Falling white-water ribbons & churning aeration streaks
	float rapids_foam = smoothstep(0.45, 0.80, flow_tex.r) * 0.60;

	float total_foam = clamp(crest_foam + impact_foam + rapids_foam, 0.0, 1.0);

	// Brilliant specular fresnel glint
	float fresnel = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 3.0);

	// Sacred mineral emerald-turquoise water color blended with white-water aeration
	vec3 base_rgb = mix(water_color.rgb, foam_color.rgb, total_foam);
	base_rgb = mix(base_rgb, vec3(0.88, 0.99, 0.97), fresnel * 0.50);

	ALBEDO = base_rgb;
	// Subtle natural radiance from sacred energized mineral water
	EMISSION = base_rgb * 0.20;
	
	// Thick, prominent optical body (solid fluid volume)
	float edge_solid = smoothstep(0.0, 0.015, UV.x) * smoothstep(1.0, 0.985, UV.x);
	ALPHA = clamp(mix(water_color.a, foam_color.a, total_foam) * edge_solid + fresnel * 0.15, 0.92, 1.0);
	
	float r_tex = mix(texture(roughness_tex, uv_fast).r, texture(roughness_tex, uv_slow).r, 0.5);
	ROUGHNESS = mix(0.02, 0.22, total_foam * r_tex);
	METALLIC = 0.04;
	SPECULAR = 0.98;
}
