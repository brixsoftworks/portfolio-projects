(() => {
  "use strict";

  const FORM = document.getElementById("contactForm");
  const STATUS = document.getElementById("formStatus");
  const SUBMIT_BTN = document.getElementById("formSubmit");
  if (!FORM || !STATUS || !SUBMIT_BTN) return;

  const CLOUDFLARE_WORKER =
    "https://floral-grass-e5d9.technologies-brix.workers.dev";

  const btnText = SUBMIT_BTN.querySelector(".btn-text");

  FORM.addEventListener("submit", async (e) => {
    e.preventDefault();
    STATUS.className = "form-status";
    STATUS.textContent = "";

    for (const el of [FORM.formName, FORM.formPhone, FORM.formEmail]) {
      el.closest(".form-group").classList.remove("error");
    }

    const name = FORM.formName.value.trim();
    const phone = FORM.formPhone.value.trim();
    const email = FORM.formEmail.value.trim();

    let valid = true;
    for (const el of [FORM.formName, FORM.formPhone, FORM.formEmail]) {
      el.closest(".form-group").classList.toggle("error", !el.value.trim());
      if (!el.value.trim()) valid = false;
    }

    if (!valid) {
      STATUS.className = "form-status error";
      STATUS.textContent = "Please fill in all fields.";
      return;
    }

    if (!/^[\d\s\-+()]{7,20}$/.test(phone)) {
      FORM.formPhone.closest(".form-group").classList.add("error");
      STATUS.className = "form-status error";
      STATUS.textContent = "Please enter a valid phone number.";
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      FORM.formEmail.closest(".form-group").classList.add("error");
      STATUS.className = "form-status error";
      STATUS.textContent = "Please enter a valid email address.";
      return;
    }

    SUBMIT_BTN.disabled = true;
    if (btnText) btnText.textContent = "Sending...";

    try {
      const data = { name, phone, email, createdAt: new Date().toISOString() };

      // Write to Firestore via Firebase SDK
      await firebase.firestore().collection("contacts").add(data);

      // Send Telegram notification via Cloudflare Worker
      await fetch(CLOUDFLARE_WORKER, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      STATUS.className = "form-status success";
      STATUS.textContent = "Thank you! We'll contact you within 24 hours.";
      FORM.reset();
    } catch {
      STATUS.className = "form-status error";
      STATUS.textContent =
        "Something went wrong. Please try again or email us directly.";
    } finally {
      SUBMIT_BTN.disabled = false;
      if (btnText) btnText.textContent = "Submit";
    }
  });
})();
