package com.strictday.enforcement

import android.app.AppOpsManager
import android.app.admin.DevicePolicyManager
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.os.Process
import android.provider.Settings
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow

@Singleton
class DeviceCapabilities @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val capabilities = MutableStateFlow(detect())

    fun flow(): Flow<DeviceCapabilitiesReport> = capabilities

    fun current(): DeviceCapabilitiesReport = capabilities.value

    fun refresh() {
        capabilities.value = detect()
    }

    private fun detect(): DeviceCapabilitiesReport {
        val pm = context.packageManager
        val dpm = context.getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
        val isOwner = dpm.isDeviceOwnerApp(context.packageName)

        return DeviceCapabilitiesReport(
            canRestrictApps = detectAppRestriction(isOwner),
            canUseUsageStats = detectUsageStats(),
            canUseAccessibility = detectAccessibility(),
            isDeviceOwner = if (isOwner) {
                DeviceCapabilitiesReport.SUPPORTED
            } else {
                DeviceCapabilitiesReport.REQUIRES_DEVICE_OWNER
            },
            canUseLockTask = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP && isOwner) {
                DeviceCapabilitiesReport.SUPPORTED
            } else {
                DeviceCapabilitiesReport.REQUIRES_DEVICE_OWNER
            },
            canControlNotifications = detectNotificationControl()
        )
    }

    /**
     * Blocking other apps' launches without device owner can only be done with a
     * foreground-service overlay. That is honestly partial, not full restriction.
     */
    private fun detectAppRestriction(isDeviceOwner: Boolean): String {
        return if (isDeviceOwner) {
            DeviceCapabilitiesReport.SUPPORTED
        } else {
            DeviceCapabilitiesReport.PARTIALLY_SUPPORTED
        }
    }

    private fun detectUsageStats(): String {
        val appOps = context.getSystemService(Context.APP_OPS_SERVICE) as AppOpsManager
        val mode = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            appOps.unsafeCheckOpNoThrow(
                AppOpsManager.OPSTR_GET_USAGE_STATS,
                Process.myUid(),
                context.packageName
            )
        } else {
            @Suppress("DEPRECATION")
            appOps.checkOpNoThrow(
                AppOpsManager.OPSTR_GET_USAGE_STATS,
                Process.myUid(),
                context.packageName
            )
        }
        return if (mode == AppOpsManager.MODE_ALLOWED) {
            DeviceCapabilitiesReport.SUPPORTED
        } else {
            DeviceCapabilitiesReport.REQUIRES_USER_PERMISSION
        }
    }

    private fun detectAccessibility(): String {
        val enabledServices = Settings.Secure.getString(
            context.contentResolver,
            Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
        ) ?: return DeviceCapabilitiesReport.REQUIRES_USER_PERMISSION

        val serviceId = "${context.packageName}/${ACCESSIBILITY_SERVICE_COMPONENT}"
        return if (enabledServices.contains(serviceId)) {
            DeviceCapabilitiesReport.SUPPORTED
        } else {
            DeviceCapabilitiesReport.REQUIRES_USER_PERMISSION
        }
    }

    private fun detectNotificationControl(): String {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) {
            return DeviceCapabilitiesReport.SUPPORTED
        }
        return if (context.checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
            == PackageManager.PERMISSION_GRANTED
        ) {
            DeviceCapabilitiesReport.SUPPORTED
        } else {
            DeviceCapabilitiesReport.REQUIRES_USER_PERMISSION
        }
    }

    private companion object {
        private const val ACCESSIBILITY_SERVICE_COMPONENT =
            "com.strictday.enforcement.StrictDayAccessibilityService"
    }
}