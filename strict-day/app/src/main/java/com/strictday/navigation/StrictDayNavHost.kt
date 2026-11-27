package com.strictday.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.strictday.ui.active.ActiveTaskScreen
import com.strictday.ui.analytics.AnalyticsScreen
import com.strictday.ui.home.HomeScreen
import com.strictday.ui.integrations.IntegrationsScreen
import com.strictday.ui.onboarding.OnboardingScreen
import com.strictday.ui.planner.NightPlannerScreen
import com.strictday.ui.schedule.ScheduleScreen
import com.strictday.ui.settings.SettingsScreen
import com.strictday.ui.task.TaskEditorScreen
import com.strictday.ui.verification.VerificationScreen

data class BottomNavItem(
    val screen: Screen,
    val label: String,
    val icon: @Composable () -> Unit
)

@Composable
fun StrictDayNavHost(
    onOnboardingComplete: () -> Unit,
    topBar: @Composable () -> Unit = {}
) {
    val navController = rememberNavController()

    val bottomNavItems = listOf(
        BottomNavItem(Screen.Home, "Home", { Icon(Icons.Default.Home, contentDescription = "Home") }),
        BottomNavItem(Screen.Schedule, "Schedule", { Icon(Icons.Default.CalendarMonth, contentDescription = "Schedule") }),
        BottomNavItem(Screen.NightPlanner, "Planner", { Icon(Icons.Default.PlayArrow, contentDescription = "Planner") }),
        BottomNavItem(Screen.Settings, "Settings", { Icon(Icons.Default.Settings, contentDescription = "Settings") })
    )

    NavHost(
        navController = navController,
        startDestination = Screen.Onboarding.route
    ) {
        composable(Screen.Onboarding.route) {
            OnboardingScreen(
                onComplete = {
                    onOnboardingComplete()
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Onboarding.route) { inclusive = true }
                    }
                }
            )
        }
        composable(Screen.Home.route) {
            HomeScreen(
                onOpenTask = { taskId -> navController.navigate(Screen.ActiveTask.createRoute(taskId)) },
                onNavigateToSchedule = { navController.navigate(Screen.Schedule.route) }
            )
        }
        composable(Screen.Schedule.route) {
            ScheduleScreen(
                onCreateTask = { navController.navigate(Screen.CreateEditTask.createRoute()) },
                onEditTask = { taskId -> navController.navigate(Screen.CreateEditTask.createRoute(taskId)) },
                onOpenPlanner = { navController.navigate(Screen.NightPlanner.route) }
            )
        }
        composable(Screen.CreateEditTask.route) { backStackEntry ->
            val taskId = backStackEntry.arguments?.getString("taskId")
            TaskEditorScreen(
                taskId = taskId?.takeIf { it != "new" },
                onDone = { navController.popBackStack() }
            )
        }
        composable(Screen.NightPlanner.route) {
            NightPlannerScreen(
                onDone = { navController.popBackStack() }
            )
        }
        composable(Screen.ActiveTask.route) { backStackEntry ->
            val taskId = backStackEntry.arguments?.getString("taskId")
            ActiveTaskScreen(
                taskId = taskId,
                onDone = { navController.popBackStack() },
                onNavigateToVerification = { navController.navigate(Screen.Verification.createRoute(it)) }
            )
        }
        composable(Screen.Verification.route) { backStackEntry ->
            val taskId = backStackEntry.arguments?.getString("taskId")
            VerificationScreen(
                taskId = taskId,
                onDone = { navController.popBackStack() }
            )
        }
        composable(Screen.Integrations.route) {
            IntegrationsScreen(onDone = { navController.popBackStack() })
        }
        composable(Screen.Analytics.route) {
            AnalyticsScreen(onDone = { navController.popBackStack() })
        }
        composable(Screen.Settings.route) {
            SettingsScreen(
                onNavigateToIntegrations = { navController.navigate(Screen.Integrations.route) },
                onNavigateToAnalytics = { navController.navigate(Screen.Analytics.route) }
            )
        }
    }
}