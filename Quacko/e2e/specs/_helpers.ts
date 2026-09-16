import { expect, type Page } from '@playwright/test';

export const MISSION_ROW = '[data-testid^="mission-row-"]';

/** Boot the app from cold: splash → auto-routes to /onboarding for a fresh demo store. */
export async function boot(page: Page) {
  await page.goto('/');
  await expect(page.getByText('QUACKO', { exact: true })).toBeVisible({ timeout: 20_000 });
  await page.waitForURL(/onboarding/, { timeout: 20_000 });
}

/** Walk the 3-step onboarding. Lands on the Today tab. */
export async function completeOnboarding(page: Page) {
  await expect(page.getByText('Meet Quacko', { exact: true })).toBeVisible();
  await page.getByText('Next', { exact: true }).click();
  await expect(page.getByText(/what are you working on\?/i)).toBeVisible();
  await page.getByText('Fitness', { exact: true }).click();
  await page.getByText('Next', { exact: true }).click();
  await expect(page.getByText('Your streak, guarded', { exact: true })).toBeVisible();
  await page.getByText('Start', { exact: true }).click();
  await expect(page.getByText(/today's missions/i)).toBeVisible({ timeout: 20_000 });
}

/** Create the demo goal and wait for today's generated mission rows. */
export async function createDemoGoal(page: Page) {
  await expect(page.getByText('No goal yet', { exact: true })).toBeVisible();
  await page.getByTestId('create-goal').click();
  await expect(page.locator(MISSION_ROW).first()).toBeVisible({ timeout: 20_000 });
}

/** Full mission golden path: start → prove → verified. Returns on Today. */
export async function completeTodayMission(page: Page) {
  await page.locator(MISSION_ROW).first().click();
  await expect(page.getByTestId('mission-start')).toBeVisible({ timeout: 10_000 });
  await page.getByTestId('mission-start').click();
  await expect(page.getByText('Mission started — focus up.', { exact: true })).toBeVisible();
  await page.getByTestId('mission-done').click();
  await expect(page.getByText('Streak day saved', { exact: true })).toBeVisible({ timeout: 15_000 });
  await page.getByTestId('mission-back').click();
  await expect(page.getByText(/today's missions/i)).toBeVisible();
}

export function assertNoHorizontalOverflow(page: Page) {
  return page.evaluate(() => {
    const doc = document.documentElement;
    return { scrollWidth: doc.scrollWidth, clientWidth: doc.clientWidth };
  });
}