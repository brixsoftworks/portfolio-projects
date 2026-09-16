"use client";

import { useState, useEffect } from "react";
import { auth } from "@/lib/firebase";
import { GoogleAuthProvider, signInWithPopup, RecaptchaVerifier, signInWithPhoneNumber, ConfirmationResult } from "firebase/auth";
import { Icon } from "@/components/icons";

export default function LoginPage() {
  const [method, setMethod] = useState<"google" | "phone">("google");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: "", type: "" });
  const [confirmationResult, setConfirmationResult] = useState<ConfirmationResult | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined" && !(window as any).recaptchaVerifier) {
      (window as any).recaptchaVerifier = new RecaptchaVerifier(auth, 'recaptcha-container', {
        size: 'invisible',
      });
    }
  }, []);

  const handleGoogleLogin = async () => {
    setLoading(true);
    setMessage({ text: "", type: "" });
    try {
      await signInWithPopup(auth, new GoogleAuthProvider());
      window.location.href = "/";
    } catch (err: any) {
      setMessage({ text: err.message || "Google login failed", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone) return;
    setLoading(true);
    setMessage({ text: "", type: "" });
    try {
      const appVerifier = (window as any).recaptchaVerifier;
      const result = await signInWithPhoneNumber(auth, phone, appVerifier);
      setConfirmationResult(result);
      setStep("otp");
      setMessage({ text: "OTP sent to your phone", type: "success" });
    } catch (err: any) {
      setMessage({ text: err.message || "Failed to send OTP", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otp || !confirmationResult) return;
    setLoading(true);
    setMessage({ text: "", type: "" });
    try {
      await confirmationResult.confirm(otp);
      window.location.href = "/";
    } catch (err: any) {
      setMessage({ text: err.message || "Invalid OTP", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center p-6 bg-[#08070a]">
      <div className="w-full max-w-md rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-lg relative overflow-hidden">
        {/* Decorative elements */}
        <div className="pointer-events-none absolute -top-24 -right-24 h-48 w-48 rounded-full bg-violet-500/20 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-24 -left-24 h-48 w-48 rounded-full bg-amber-500/20 blur-3xl" />

        <div className="relative z-10 text-center mb-8">
          <h1 className="text-3xl font-bold mb-2 text-white" style={{ fontFamily: "var(--font-cormorant), Georgia, serif" }}>
            Welcome
          </h1>
          <p className="text-sm text-white/50">
            Sign in to access your festive collections
          </p>
        </div>

        {message.text && (
          <div
            className={`mb-6 p-3 rounded-xl text-sm text-center ${
              message.type === "error"
                ? "bg-red-500/10 text-red-400 border border-red-500/20"
                : "bg-green-500/10 text-green-400 border border-green-500/20"
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Tab Selection */}
        <div className="flex gap-2 mb-8 bg-white/5 p-1 rounded-xl border border-white/5">
          <button
            onClick={() => {
              setMethod("google");
              setStep("phone");
              setMessage({ text: "", type: "" });
            }}
            className={`flex-1 py-2 text-sm font-medium rounded-lg transition-colors ${
              method === "google"
                ? "bg-white/10 text-white shadow"
                : "text-white/50 hover:text-white"
            }`}
          >
            Google
          </button>
          <button
            onClick={() => {
              setMethod("phone");
              setMessage({ text: "", type: "" });
            }}
            className={`flex-1 py-2 text-sm font-medium rounded-lg transition-colors ${
              method === "phone"
                ? "bg-white/10 text-white shadow"
                : "text-white/50 hover:text-white"
            }`}
          >
            Phone
          </button>
        </div>

        {method === "google" && (
          <div className="space-y-4">
            <button
              onClick={handleGoogleLogin}
              disabled={loading}
              className="w-full flex items-center justify-center gap-3 rounded-xl bg-white text-black px-4 py-3.5 font-medium transition-transform hover:scale-[0.98] active:scale-95 disabled:opacity-50 disabled:hover:scale-100"
            >
              {loading ? (
                <span className="h-5 w-5 animate-spin rounded-full border-2 border-black/20 border-t-black" />
              ) : (
                <svg className="h-5 w-5" viewBox="0 0 24 24">
                  <path
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    fill="#4285F4"
                  />
                  <path
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    fill="#34A853"
                  />
                  <path
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    fill="#EA4335"
                  />
                </svg>
              )}
              Continue with Google
            </button>
          </div>
        )}

        {method === "phone" && step === "phone" && (
          <form onSubmit={handleSendOtp} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide text-white/50 mb-1.5">
                Phone Number
              </label>
              <input
                type="tel"
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+91 98765 43210"
                className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-white/30 outline-none focus:border-violet-500/50 focus:bg-white/10 transition-colors"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !phone}
              className="w-full rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-500 px-4 py-3.5 font-bold text-white transition hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[0.98] active:scale-95"
            >
              {loading ? "Sending..." : "Send OTP"}
            </button>
          </form>
        )}

        {method === "phone" && step === "otp" && (
          <form onSubmit={handleVerifyOtp} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide text-white/50 mb-1.5">
                Enter OTP
              </label>
              <input
                type="text"
                required
                maxLength={6}
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="000000"
                className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-center tracking-[0.5em] text-2xl text-white placeholder:text-white/30 outline-none focus:border-violet-500/50 focus:bg-white/10 transition-colors"
              />
            </div>
            <button
              type="submit"
              disabled={loading || otp.length < 6}
              className="w-full rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-500 px-4 py-3.5 font-bold text-white transition hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[0.98] active:scale-95"
            >
              {loading ? "Verifying..." : "Verify & Login"}
            </button>
            <button
              type="button"
              onClick={() => {
                setStep("phone");
                setOtp("");
                setMessage({ text: "", type: "" });
              }}
              className="w-full text-sm text-white/50 hover:text-white transition-colors py-2"
            >
              Back
            </button>
          </form>
        )}
      </div>
      <div id="recaptcha-container"></div>
    </main>
  );
}
