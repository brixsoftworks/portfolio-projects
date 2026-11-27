package com.strictday.ui.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

private val Primary = Color(0xFF7C4DFF)
private val Secondary = Color(0xFF03DAC6)
private val Error = Color(0xFFCF6679)
private val Background = Color(0xFF0D0D0F)
private val Surface = Color(0xFF16161A)

val DarkColors = darkColorScheme(
    primary = Primary,
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFF2B1956),
    onPrimaryContainer = Color(0xFFE7DFFF),
    inversePrimary = Color(0xFF9A7BFF),
    secondary = Secondary,
    onSecondary = Color(0xFF00201A),
    secondaryContainer = Color(0xFF00483D),
    onSecondaryContainer = Color(0xFF7CFFF0),
    tertiary = Color(0xFF8AB4F8),
    onTertiary = Color(0xFF002256),
    tertiaryContainer = Color(0xFF0A3A77),
    onTertiaryContainer = Color(0xFFD3E4FF),
    background = Background,
    onBackground = Color(0xFFE2E2E6),
    surface = Surface,
    onSurface = Color(0xFFE2E2E6),
    surfaceVariant = Color(0xFF2A2A31),
    onSurfaceVariant = Color(0xFFC4C4CC),
    surfaceTint = Primary,
    inverseSurface = Color(0xFFE2E2E6),
    inverseOnSurface = Color(0xFF16161A),
    error = Error,
    onError = Color(0xFF3A0811),
    errorContainer = Color(0xFF4A1620),
    onErrorContainer = Color(0xFFFFDADF),
    outline = Color(0xFF8A8A93),
    outlineVariant = Color(0xFF3F3F46),
    scrim = Color(0xFF000000),
    surfaceBright = Color(0xFF3C3C44),
    surfaceContainer = Color(0xFF1C1C22),
    surfaceContainerHigh = Color(0xFF26262D),
    surfaceContainerHighest = Color(0xFF313138),
    surfaceContainerLow = Color(0xFF121216),
    surfaceContainerLowest = Color(0xFF08080A)
)

val LightColors = lightColorScheme(
    primary = Primary,
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFE7DFFF),
    onPrimaryContainer = Color(0xFF1F0F4A),
    inversePrimary = Color(0xFFB7A5FF),
    secondary = Secondary,
    onSecondary = Color(0xFFFFFFFF),
    secondaryContainer = Color(0xFF7CFFF0),
    onSecondaryContainer = Color(0xFF00332B),
    tertiary = Color(0xFF4B6FE0),
    onTertiary = Color(0xFFFFFFFF),
    tertiaryContainer = Color(0xFFDBDFFF),
    onTertiaryContainer = Color(0xFF00175B),
    background = Color(0xFFFAF9FB),
    onBackground = Color(0xFF1B1B1F),
    surface = Color(0xFFFAF9FB),
    onSurface = Color(0xFF1B1B1F),
    surfaceVariant = Color(0xFFE2E1E9),
    onSurfaceVariant = Color(0xFF45464F),
    surfaceTint = Primary,
    inverseSurface = Color(0xFF302F36),
    inverseOnSurface = Color(0xFFF2F0F8),
    error = Error,
    onError = Color(0xFFFFFFFF),
    errorContainer = Color(0xFFFFDADF),
    onErrorContainer = Color(0xFF3A0811),
    outline = Color(0xFF767680),
    outlineVariant = Color(0xFFC6C5D0),
    scrim = Color(0xFF000000),
    surfaceBright = Color(0xFFFAF9FB),
    surfaceContainer = Color(0xFFEEEDF2),
    surfaceContainerHigh = Color(0xFFE8E7EC),
    surfaceContainerHighest = Color(0xFFE2E1E6),
    surfaceContainerLow = Color(0xFFF4F3F8),
    surfaceContainerLowest = Color(0xFFFFFFFF)
)