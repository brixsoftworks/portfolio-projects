import { test, expect } from '@playwright/test';
import { boot, completeOnboarding, createDemoGoal, assertNoHorizontalOverflow } from './_helpers';

test.describe('UI/UX navigation & presentation', () => {
  test('tab bar is present and visits every destination', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);

    for (const [label, marker] of [
      ['Today', "today's missions"],
      ['Chat', 'quacko coach'],
      ['Explore', 'The Quacko universe'],
      ['Profile', 'Demo Ducky'],
    ] as const) {
      await page.getByText(label, { exact: true }).click();
      await expect(page.getByText(marker)).toBeVisible({ timeout: 10_000 });
    }
  });

  test('no uncaught page errors across the main flows', async ({ page }) => {
    const pageErrors: string[] = [];
    page.on('pageerror', (err) => pageErrors.push(err.message));

    await boot(page);
    await completeOnboarding(page);
    await createDemoGoal(page);

    for (const tab of ['Today', 'Chat', 'Explore', 'Profile']) {
      await page.getByText(tab, { exact: true }).click();
    }
    await page.getByText('Today', { exact: true }).click();
    await page.locator('[data-testid^="mission-row-"]').first().click();
    await expect(page.getByTestId('mission-back')).toBeVisible();
    await page.getByTestId('mission-back').click();

    expect(pageErrors, `page errors: ${pageErrors.join('; ')}`).toHaveLength(0);
  });

  test('inactive tab scenes are hidden — no cross-tab bleed', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    await createDemoGoal(page);

    await page.getByText('Chat', { exact: true }).click();
    // A Today-only element must not be visually rendered while Chat is active.
    await expect(page.getByText('Keep the chain alive.')).not.toBeVisible();
    await expect(page.getByPlaceholder('Message Quacko…')).toBeVisible();

    await page.getByText('Profile', { exact: true }).click();
    await expect(page.getByText('Keep the chain alive.')).not.toBeVisible();
    await expect(page.getByText('Demo Ducky', { exact: true })).toBeVisible();
  });

  test('mission buttons are keyboard-focusable and honor disabled semantics', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    await createDemoGoal(page);
    await page.locator('[data-testid^="mission-row-"]').first().click();
    await expect(page.getByTestId('mission-start')).toBeVisible();

    const startTabIndex = await page.getByTestId('mission-start').getAttribute('tabindex');
    expect(startTabIndex).toBe('0');

    await page.getByTestId('mission-start').click();
    await expect(page.getByTestId('mission-start')).toHaveAttribute('aria-disabled', 'true');
    await expect(page.getByTestId('mission-done')).toBeEnabled();
  });

  test('dark Neon Tokyo theme is applied on every screen', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    for (const tab of ['Today', 'Chat', 'Explore', 'Profile']) {
      await page.getByText(tab, { exact: true }).click();
      // Night-gradient nebula backdrop fills the viewport everywhere.
      const backdrop = page.locator('[data-testid="backdrop"]:visible');
      await expect(backdrop.first()).toBeVisible();
      const bgImage = await backdrop.first().evaluate((el) => getComputedStyle(el).backgroundImage);
      expect(bgImage, `backdrop on ${tab}`).toContain('linear-gradient');
    }
  });
});

test.describe('Responsive layout', () => {
  test('no horizontal overflow on a phone-sized viewport', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    await createDemoGoal(page);

    for (const tab of ['Today', 'Chat', 'Explore', 'Profile']) {
      await page.getByText(tab, { exact: true }).click();
      await page.waitForTimeout(400);
      const { scrollWidth, clientWidth } = await assertNoHorizontalOverflow(page);
      expect(scrollWidth, `overflow on ${tab}: ${scrollWidth} > ${clientWidth}`).toBeLessThanOrEqual(clientWidth);
    }
  });

  test('empty state fits and scrolls without clipping action CTA', async ({ page }) => {
    await boot(page);
    await completeOnboarding(page);
    await expect(page.getByTestId('create-goal')).toBeVisible();
    const box = await page.getByTestId('create-goal').boundingBox();
    expect(box).not.toBeNull();
    expect(box!.width, 'button wider than viewport').toBeLessThanOrEqual(390);
  });
});