// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
// Adapted from AmazonAppDev/hello-world-fire-tv (see THIRD_PARTY_NOTICES.md): package renamed, TV dark scheme only.

package com.afc.companion.ui.theme

import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Typography
import androidx.tv.material3.darkColorScheme

private val Purple80 = Color(0xFFD0BCFF)
private val PurpleGrey80 = Color(0xFFCCC2DC)
private val Pink80 = Color(0xFFEFB8C8)
private val Black = Color(0xFF030303)

// Couch UI: body text stays at or above 24 px at 1080p (AFC-PR-045).
private val AfcTypography = Typography(
    bodyLarge = TextStyle(fontFamily = FontFamily.Default, fontWeight = FontWeight.Normal, fontSize = 16.sp, lineHeight = 24.sp, letterSpacing = 0.5.sp),
)

@Composable
fun AfcTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = darkColorScheme(primary = Purple80, secondary = PurpleGrey80, tertiary = Pink80, background = Black, surfaceVariant = Color.LightGray),
        typography = AfcTypography,
        content = content,
    )
}
