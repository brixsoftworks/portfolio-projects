package com.strictday.data.remote

import com.strictday.BuildConfig

/**
 * Runtime configuration for the optional Supabase sync layer.
 *
 * Values are compiled into BuildConfig and default to disabled/empty. To enable
 * sync, set the three fields below in `app/build.gradle.kts` (or via a per-build
 * flavor) and provide a runtime Supabase session token (see SessionTokenStore).
 */
object RemoteConfig {

    const val supabaseUrl: String = BuildConfig.SUPABASE_URL
    const val supabaseAnonKey: String = BuildConfig.SUPABASE_ANON_KEY
    const val syncEnabled: Boolean = BuildConfig.SUPABASE_SYNC_ENABLED

    val isConfigured: Boolean
        get() = syncEnabled && supabaseUrl.isNotBlank() && supabaseAnonKey.isNotBlank()
}