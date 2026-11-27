package com.strictday.enforcement

import android.app.admin.DevicePolicyManager
import android.content.ComponentName
import android.content.Context
import android.os.Bundle
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AppRestrictionManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val deviceCapabilities: DeviceCapabilities
) {
    fun setAppRestrictions(packageName: String, blocked: Boolean): Boolean {
        val caps = deviceCapabilities.current()
        if (caps.canRestrictApps != DeviceCapabilitiesReport.SUPPORTED) return false

        val admin = adminComponent() ?: return false
        val dpm = context.getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
        // Requires device-owner privileges: DPM.setApplicationRestrictions may only be
        // called by the active device owner and only affects the target package.
        dpm.setApplicationRestrictions(
            admin,
            packageName,
            Bundle().apply {
                if (blocked) putBoolean("strict_day.blocked", true)
            }
        )
        return true
    }

    private fun adminComponent(): ComponentName? {
        return try {
            val component = ComponentName(context, StrictDayDeviceAdminReceiver::class.java)
            val dpm = context.getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
            if (dpm.isAdminActive(component)) component else null
        } catch (_: Exception) {
            null
        }
    }
}