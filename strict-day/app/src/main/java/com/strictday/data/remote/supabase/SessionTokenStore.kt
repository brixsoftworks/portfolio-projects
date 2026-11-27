package com.strictday.data.remote.supabase

import javax.inject.Inject
import javax.inject.Singleton

/**
 * Holds the current Supabase access token used for authenticated Postgrest
 * requests. Set by the application once a user session exists (populated from
 * UserPreferences at sync time). Requests carry the token only while it is set;
 * an empty token means unauthenticated, and RLS on the server rejects writes.
 */
@Singleton
class SessionTokenStore @Inject constructor() {

    @Volatile
    var token: String = ""
        private set

    fun update(token: String) {
        this.token = token
    }

    fun clear() {
        token = ""
    }
}