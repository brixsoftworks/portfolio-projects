package com.strictday.navigation

sealed class Screen(val route: String) {
    data object Onboarding : Screen("onboarding")
    data object Home : Screen("home")
    data object Schedule : Screen("schedule")
    data object CreateEditTask : Screen("task/{taskId}") {
        fun createRoute(taskId: String? = null): String = "task/${taskId ?: "new"}"
    }
    data object NightPlanner : Screen("planner")
    data object ActiveTask : Screen("active/{taskId}") {
        fun createRoute(taskId: String): String = "active/$taskId"
    }
    data object Verification : Screen("verification/{taskId}") {
        fun createRoute(taskId: String): String = "verification/$taskId"
    }
    data object Integrations : Screen("integrations")
    data object Analytics : Screen("analytics")
    data object Settings : Screen("settings")
}