import { test, expect } from "@playwright/test"

async function load(page) {
  await page.goto("/", { waitUntil: "domcontentloaded" })
  await page.waitForTimeout(1500)
}

test("all section ids exist on the page", async ({ page }) => {
  await load(page)
  const ids = ["home", "placements", "teaching-learning", "student-services", "quick-links", "highlights", "voice", "explore-more", "photo-gallery", "info", "contact"]
  for (const id of ids) {
    await expect(page.locator(`#${id}`)).toBeVisible()
  }
})

test.describe("navbar top-level navigation", () => {
  const tests = [
    { label: "Home", href: "#home" },
    { label: "Placements", href: "#placements" },
    { label: "Contact", href: "#contact" },
  ]
  for (const { label, href } of tests) {
    test(`"${label}" scrolls to ${href}`, async ({ page }) => {
      await load(page)
      await page.click(`nav a[href="${href}"]`)
      await page.waitForTimeout(1200)
      const el = page.locator(href)
      await expect(el).toBeVisible()
    })
  }
})

test.describe("navbar dropdown navigation", () => {
  const tests = [
    { parent: "About", child: "About College", href: "#highlights" },
    { parent: "Academics", child: "School of Computer Studies", href: "#highlights" },
    { parent: "Academics", child: "E-Content", href: "#explore-more" },
    { parent: "Admissions", child: "Online Application", href: "#student-services" },
    { parent: "Research", child: "Research Policy", href: "#info" },
    { parent: "Campus Life", child: "Photo Gallery", href: "#photo-gallery" },
  ]
  for (const { parent, child, href } of tests) {
    test(`"${parent} > ${child}" scrolls to ${href}`, async ({ page }) => {
      await load(page)
      await page.getByText(parent, { exact: true }).first().hover()
      await page.waitForTimeout(300)
      await page.locator("nav").getByText(child, { exact: true }).first().click()
      await page.waitForTimeout(1200)
      const el = page.locator(href)
      await expect(el).toBeVisible({ timeout: 5000 })
    })
  }
})

test("logo scrolls to home", async ({ page }) => {
  await load(page)
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
  await page.waitForTimeout(500)
  await page.click("nav a[href='#home']")
  await page.waitForTimeout(1200)
  await expect(page.locator("#home")).toBeVisible()
})

test("mobile menu works", async ({ page }) => {
  await load(page)
  await page.setViewportSize({ width: 600, height: 800 })
  const menuBtn = page.locator("nav button").first()
  await menuBtn.click()
  await page.waitForTimeout(400)
  await page.locator("nav a[href='#placements']").last().click()
  await page.waitForTimeout(1200)
  await expect(page.locator("#placements")).toBeVisible()
})

test.describe("external links in sections", () => {
  test("Explore Programs links to admissions portal", async ({ page }) => {
    await load(page)
    const link = page.locator('a[href="https://admissions.rvscas.ac.in/"]').first()
    await expect(link).toBeVisible()
    expect(await link.getAttribute("target")).toBe("_blank")
  })

  test("Virtual Tour links to YouTube", async ({ page }) => {
    await load(page)
    const link = page.locator('a[href="https://youtu.be/6Z3jYxlyvww"]').first()
    await expect(link).toBeVisible()
    expect(await link.getAttribute("target")).toBe("_blank")
  })

  test("View Placement Report links to /placement/records", async ({ page }) => {
    await load(page)
    const link = page.locator('a[href="https://rvscas.ac.in/placement/records"]').first()
    await expect(link).toBeVisible()
  })

  test("Placement Gallery links to /placement/gallery", async ({ page }) => {
    await load(page)
    const link = page.locator('a[href="https://rvscas.ac.in/placement/gallery"]').first()
    await expect(link).toBeVisible()
  })

  test("QuickLinks have valid hrefs", async ({ page }) => {
    await load(page)
    await expect(page.locator('a[href="https://rvscas.ac.in/nirf"]')).toBeVisible()
    await expect(page.locator('a[href*="SSR-Fourth"]')).toBeVisible()
    await expect(page.locator('a[href="https://rvscas.ac.in/iqac"]')).toBeVisible()
    await expect(page.locator('a[href="https://rvscas.directverify.in/student/#/app/request"]')).toBeVisible()
  })

  test("Footer social links have correct URLs", async ({ page }) => {
    await load(page)
    await expect(page.locator('a[href="https://youtube.com/c/RVSCASSulurCoimbatore"]')).toBeVisible()
    await expect(page.locator('a[href="https://www.instagram.com/rvssulur.cas/"]')).toBeVisible()
    await expect(page.locator('a[href="https://www.facebook.com/rvssulur.cas/"]')).toBeVisible()
    await expect(page.locator('a[href="https://www.linkedin.com/company/rvssulur-cas/"]')).toBeVisible()
  })

  test("Footer NPTEL, Swayam, Vidya-Mitra links exist", async ({ page }) => {
    await load(page)
    await expect(page.locator('a[href="https://nptel.ac.in/"]').first()).toBeVisible()
    await expect(page.locator('a[href="https://swayam.gov.in/"]').first()).toBeVisible()
    await expect(page.locator('a[href="https://vidyamitra.inflibnet.ac.in/"]').first()).toBeVisible()
  })

  test("ExploreMore Quiz Club links to campus/quiz", async ({ page }) => {
    await load(page)
    await expect(page.locator('a[href="https://rvscas.ac.in/campus/quiz"]')).toBeVisible()
  })

  test("Student Services all 4 links open externally", async ({ page }) => {
    await load(page)
    const section = page.locator("#student-services")
    const links = section.locator("a")
    expect(await links.count()).toBe(4)
    for (let i = 0; i < 4; i++) {
      expect(await links.nth(i).getAttribute("target")).toBe("_blank")
    }
  })

  test("Photo Gallery has real image src", async ({ page }) => {
    await load(page)
    const imgs = page.locator("#photo-gallery img")
    expect(await imgs.count()).toBe(6)
    for (let i = 0; i < 6; i++) {
      const src = await imgs.nth(i).getAttribute("src")
      expect(src).toContain("rvscas.ac.in/images/gallery/")
    }
  })

  test("TeachingLearning Learn More links to best practice", async ({ page }) => {
    await load(page)
    await expect(page.locator('a[href="https://rvscas.ac.in/academics/academic-insights/bestpractice"]')).toBeVisible()
  })

  test("InfoSection items are clickable links", async ({ page }) => {
    await load(page)
    const section = page.locator("#info")
    const links = section.locator("a[href]")
    expect(await links.count()).toBeGreaterThanOrEqual(7)
  })
})

test.describe("all anchors have no bare #", () => {
  test("no placeholder links remain in main content", async ({ page }) => {
    await load(page)
    const links = page.locator("section a[href='#'], footer a[href='#']")
    expect(await links.count()).toBe(0)
  })
})
