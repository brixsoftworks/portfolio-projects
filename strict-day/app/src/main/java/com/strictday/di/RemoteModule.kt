package com.strictday.di

import com.strictday.data.remote.RemoteConfig
import com.strictday.data.remote.supabase.SessionTokenStore
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import io.github.jan.supabase.SupabaseClient
import io.github.jan.supabase.createSupabaseClient
import io.github.jan.supabase.functions.Functions
import io.github.jan.supabase.postgrest.Postgrest
import javax.inject.Singleton

/**
 * Provides the Supabase client when sync is enabled and configured. Returns
 * null otherwise, so the rest of the app runs as a local-only build.
 *
 * The [accessToken] lambda is invoked by the SDK for every request and
 * supplies whatever token the app currently holds - so the client reacts to
 * sign-in/sign-out without being rebuilt.
 */
@Module
@InstallIn(SingletonComponent::class)
object RemoteModule {

    @Provides
    @Singleton
    fun provideSupabaseClient(tokenStore: SessionTokenStore): SupabaseClient? {
        if (!RemoteConfig.isConfigured) return null
        return createSupabaseClient(
            supabaseUrl = RemoteConfig.supabaseUrl,
            supabaseKey = RemoteConfig.supabaseAnonKey,
        ) {
            install(Postgrest)
            install(Functions)
            accessToken = { tokenStore.token }
        }
    }
}