import { test, expect } from '@playwright/test';
import { assertNoHorizontalOverflow, boot, completeOnboarding } from './_helpers';

test.describe('Onboarding & first run', () => {
  test('splash boots and routes a fresh user to onboarding', async ({ page }) => {
    await boot(page);
    await expect(page.getByText('Meet Quacko', { exact: true })).toBeVisible();
    await expect(page.getByText(/high-energy streak coach/i)).toBeVisible();
  });

  test('onboarding completes and lands on Today', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    await expect(page.getByText('Hi, Demo 👋', { exact: true })).toBeVisible();
  });

  test('onboarding shows the area picker and streak-guard copy', async ({ page }) => {
    await boot(page);
    await page.getByText('Next', { exact: true }).click();
    for (const area of ['Fitness', 'Learning', 'Skills', 'Reading', 'Wellbeing', 'Digital habits']) {
      await expect(page.getByText(area, { exact: true })).toBeVisible();
    }
    await page.getByText('Next', { exact: true }).click();
    await expect(page.getByText(/2 grace days and a shield/)).toBeVisible();
  });

  test('today tab shows the empty state and asks for a goal', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    await expect(page.getByText('No goal yet', { exact: true })).toBeVisible();
    await expect(page.getByText('Create demo goal', { exact: true })).toBeVisible();
    await expect(page.getByTestId('header-streak')).toHaveText('0');
  });
});

test.describe('Empty-state visuals', () => {
  test('fresh viewport fits with no horizontal overflow', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    const { scrollWidth, clientWidth } = await assertNoHorizontalOverflow(page);
    expect(scrollWidth, `scrollWidth ${scrollWidth} > clientWidth ${clientWidth}`).toBeLessThanOrEqual(clientWidth);
  });
});