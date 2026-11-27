shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;

uniform sampler2D mud_albedo : source_color, filter_linear_mipmap_anisotropic;
uniform sampler2D mud_normal : hint_normal, filter_linear_mipmap_anisotropic;
uniform sampler2D mud_roughness : hint_default_white, filter_linear_mipmap_anisotropic;

uniform sampler2D grass_albedo : source_color, filter_linear_mipmap_anisotropic;
uniform sampler2D grass_normal : hint_normal, filter_linear_mipmap_anisotropic;
uniform sampler2D grass_roughness : hint_default_white, filter_linear_mipmap_anisotropic;

uniform vec2 uv_scale = vec2(0.20, 0.20);

varying vec3 v_world_pos;
varying vec3 v_world_normal;

float continuous_noise(vec2 p) {
    // 37-degree rotation to break axis alignment & eliminate grid banding
    vec2 pr = vec2(p.x * 0.798 - p.y * 0.602, p.x * 0.602 + p.y * 0.798);
    float v = sin(pr.x * 0.073 + pr.y * 0.041) * 0.38;
    v += cos(pr.x * 0.137 - pr.y * 0.119 + 1.2) * 0.26;
    v += sin(pr.x * 0.271 + pr.y * 0.233 + 2.7) * 0.18;
    v += cos(pr.x * 0.511 - pr.y * 0.473 + 0.5) * 0.12;
    v += sin(pr.x * 1.130 + pr.y * 0.970) * 0.06;
    return v * 0.5 + 0.5;
}

void vertex() {
    v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    v_world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
    vec2 uv_mud = v_world_pos.xz * uv_scale;
    vec2 uv_grass_macro = v_world_pos.xz * (uv_scale * 0.85) + vec2(0.31, 0.67);
    vec2 uv_grass_micro = v_world_pos.xz * (uv_scale * 4.50) + vec2(0.12, 0.48);

    vec4 c_mud_raw = texture(mud_albedo, uv_mud);
    vec3 c_mud = c_mud_raw.rgb * vec3(0.52, 0.40, 0.30) + vec3(0.05, 0.035, 0.025);
    vec3 n_mud = texture(mud_normal, uv_mud).rgb * 2.0 - 1.0;
    float r_mud = texture(mud_roughness, uv_mud).r;

    vec4 c_grass_macro = texture(grass_albedo, uv_grass_macro);
    vec4 c_grass_micro = texture(grass_albedo, uv_grass_micro);
    vec3 grass_blended = mix(c_grass_macro.rgb, c_grass_micro.rgb, 0.40) * 1.15;
    vec3 c_grass = grass_blended * vec3(0.86, 1.06, 0.76);
    vec3 n_grass = (texture(grass_normal, uv_grass_macro).rgb + texture(grass_normal, uv_grass_micro).rgb * 0.5) * 1.33 - 1.0;
    float r_grass = mix(texture(grass_roughness, uv_grass_macro).r, texture(grass_roughness, uv_grass_micro).r, 0.5);

    float n_val = continuous_noise(v_world_pos.xz * 0.16);
    float n_micro = continuous_noise(v_world_pos.xz * 0.85);
    float n_organic = n_val * 0.70 + n_micro * 0.30;

    float wx = v_world_pos.x;
    float wz = v_world_pos.z;
    float curb_fade = 1.0;

    // Suppress grass on Malai Vasal forecourt & threshold: Z in [565, 595], |X| <= 36
    if (wz >= 565.0 && wz <= 595.0 && abs(wx) <= 36.0) {
        curb_fade = 0.0;
    }

    // Suppress grass on 20m walkway in front: Z in [113, 575], |X| <= 10.2
    if (wz >= 113.0 && wz <= 575.0 && abs(wx) <= 10.2) {
        curb_fade = 0.0;
    }

    // Suppress grass on Adiyogi stepped plaza & courtyard: Z in [-36, 113.5], |X| <= 40.5
    float courtyard_fade = 1.0;
    if (wz >= -36.0 && wz <= 113.5 && abs(wx) <= 40.5) {
        courtyard_fade = 0.0;
    }

    // Suppress grass on Suryakund temple precinct (red laterite mud apron, rotated -8.26 deg)
    float r_sk_x = wx - (-377.30);
    float r_sk_z = wz - (-603.42);
    float rad_sk = 0.14416; // -(-8.26 deg) in radians
    float cos_sk = cos(rad_sk);
    float sin_sk = sin(rad_sk);
    float l_sk_x = abs(r_sk_x * cos_sk - r_sk_z * sin_sk);
    float l_sk_z = abs(r_sk_x * sin_sk + r_sk_z * cos_sk);
    float suryakund_fade = 1.0;
    if (l_sk_x <= 85.0 && l_sk_z <= 85.0) {
        suryakund_fade = 0.0;
    } else if (l_sk_x < 120.0 && l_sk_z < 120.0) {
        float bx = max(0.0, l_sk_x - 85.0) / 35.0;
        float bz = max(0.0, l_sk_z - 85.0) / 35.0;
        suryakund_fade = clamp(max(bx, bz), 0.0, 1.0);
    }

    // Pilgrimage processional trail: Leg 1 (Adiyogi to Sarpa Vasal) & Leg 2 (Sarpa Vasal to Suryakund)
    vec2 p_start = vec2(-35.0, 25.0);
    vec2 p_sv = vec2(-393.94, -431.26);
    vec2 p_end = vec2(-388.61, -525.49);

    // Leg 1: Adiyogi -> Sarpa Vasal (bearing 42.42 deg, pointing straight between Adiyogi and Sarpa Vasal)
    vec2 line1 = p_sv - p_start;
    float len1_sq = dot(line1, line1);
    float t1 = clamp(dot(vec2(wx, wz) - p_start, line1) / len1_sq, 0.0, 1.0);
    // Gentle meander that straightens out into Sarpa Vasal
    float meander1 = (sin(t1 * 12.0) * 4.0 + cos(t1 * 24.0) * 1.8) * (1.0 - smoothstep(0.65, 0.95, t1));
    vec2 norm1 = normalize(vec2(-line1.y, line1.x));
    vec2 proj1 = p_start + t1 * line1 + norm1 * meander1;
    float dist1 = length(vec2(wx, wz) - proj1);

    // Leg 2: Sarpa Vasal -> Suryakund (leaving rear of gate towards kund complex)
    vec2 line2 = p_end - p_sv;
    float len2_sq = dot(line2, line2);
    float t2 = clamp(dot(vec2(wx, wz) - p_sv, line2) / len2_sq, 0.0, 1.0);
    vec2 proj2 = p_sv + t2 * line2;
    float dist2 = length(vec2(wx, wz) - proj2);

    float trail_dist = min(dist1, dist2);
    // Trail width ~10m with soft natural earthen transition
    float trail_fade = smoothstep(5.0, 14.0, trail_dist);

    float grass_factor = smoothstep(0.12, 0.32, n_organic) * curb_fade * courtyard_fade * suryakund_fade * trail_fade;

    ALBEDO = mix(c_mud, c_grass, grass_factor);
    NORMAL_MAP = mix(n_mud, n_grass, grass_factor) * 0.5 + 0.5;
    NORMAL_MAP_DEPTH = 1.35;
    ROUGHNESS = mix(r_mud, r_grass, grass_factor);
    SPECULAR = 0.12;
}
