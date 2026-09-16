import { test, expect } from '@playwright/test';
import { boot, completeOnboarding, createDemoGoal, completeTodayMission, MISSION_ROW } from './_helpers';

test.describe('Golden path: goal → mission → proof → streak/XP', () => {
  test('creating a goal generates today missions with proof payloads', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    await createDemoGoal(page);

    await expect(page.locator(MISSION_ROW).first()).toBeVisible();
    await expect(page.getByText(/min · proof:/).first()).toBeVisible();
    expect(await page.locator(MISSION_ROW).count()).toBeGreaterThan(0);
    await expect(page.getByText('available', { exact: true }).first()).toBeVisible();
    await expect(page.getByTestId('header-streak')).toHaveText('0');
  });

  test('full mission cycle pays a streak day and XP', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    await createDemoGoal(page);

    await completeTodayMission(page);

    await expect(page.getByTestId('header-streak')).toHaveText('1');
    await expect(page.locator('[data-testid^="mission-row-"]').first()).toContainText('verified');
  });

  test('mission detail guards lifecycle: start locks, no double proof', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    await createDemoGoal(page);

    await page.locator('[data-testid^="mission-row-"]').first().click();
    await expect(page.getByTestId('mission-start')).toBeVisible();
    await expect(page.getByTestId('mission-done')).toBeEnabled();

    // Start → that button must lock while "I did it" stays available
    await page.getByTestId('mission-start').click();
    await expect(page.getByTestId('mission-start')).toHaveAttribute('aria-disabled', 'true');

    // Prove it
    await page.getByTestId('mission-done').click();
    await expect(page.getByText('Streak day saved', { exact: true })).toBeVisible();
    await expect(page.getByTestId('mission-done')).toHaveAttribute('aria-disabled', 'true'); // verified → cannot re-prove
    await expect(page.getByText('verified', { exact: true })).toBeVisible();
  });

  test('mission back button returns to Today', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    await createDemoGoal(page);
    await page.locator('[data-testid^="mission-row-"]').first().click();
    await expect(page.getByTestId('mission-back')).toBeVisible();
    await page.getByTestId('mission-back').click();
    await expect(page.getByText("today's missions")).toBeVisible();
  });

  test('chat reflects goal context and echoes user messages', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    await createDemoGoal(page);

    await page.getByText('Chat', { exact: true }).click();
    await expect(page.getByText(/quacko coach/i)).toBeVisible();
    await expect(page.getByText(/Quack! I'm your coach/)).toBeVisible();

    await page.getByPlaceholder('Message Quacko…').fill('How is my streak?');
    await page.keyboard.press('Enter');
    await expect(page.getByText('How is my streak?', { exact: true })).toBeVisible();

    // The demo coach replies deterministically with streak-aware copy.
    await expect(page.getByText(/Show up today and it counts\.|Keep the chain alive\./).last()).toBeVisible({ timeout: 10_000 });
  });

  test('explore presents the six core feature cards', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    await page.getByText('Explore', { exact: true }).click();
    await expect(page.getByText('The Quacko universe', { exact: true })).toBeVisible();
    for (const feature of ['Battles', 'Punishment Council', 'Group AI coach', 'Learning plans', 'Proof verification', 'Active tracking']) {
      await expect(page.getByText(feature, { exact: true })).toBeVisible();
    }
  });

  test('profile reflects level, XP and the goal', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    await createDemoGoal(page);
    await completeTodayMission(page);

    await page.getByText('Profile', { exact: true }).click();
    await expect(page.getByText('Demo Ducky', { exact: true })).toBeVisible();
    await expect(page.getByText(/@ducky/)).toBeVisible();
    await expect(page.getByText('Level 1', { exact: true })).toBeVisible();
    await expect(page.getByText(/XP ·/)).toBeVisible();
    await expect(page.getByText(/Run a little every day/i)).toBeVisible();
    await expect(page.getByText(/Demo backend running/)).toBeVisible();
  });

  test('goal progress and title backdate after a proved day', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    await createDemoGoal(page);
    await completeTodayMission(page);

    await page.getByText('Profile', { exact: true }).click();
    await expect(page.getByText(/Fresh Ducky/)).toBeVisible();
    await expect(page.getByText(/\d+%/, { exact: false }).first()).toBeVisible();
  });
});