# Strict Day: Server-Authoritative Schedule Enforcement Android Engine

**Lead Systems Architect:** Mullainathan (`mullainathan95@gmail.com`)  
**Organization:** Brix Softworks  
**Role:** Principal Systems Architect & Senior Software Engineer  
**Target Platform:** Android SDK 35 (Kotlin 2.1, Jetpack Compose, Hilt, Room, Supabase)  
**Repository Status:** Production / Fully Functional  

---

## Executive Summary

Strict Day is a native Android operating system scheduling engine engineered with an uncompromising server-authoritative enforcement model. The system strictly isolates device application access during designated commitment windows, enforcing a linear execution pipeline:

```text
SCHEDULE  -->  LOCK  -->  WORK  -->  VERIFY  -->  UNLOCK
```

Unlike client-controlled productivity timers that can be bypassed or manipulated locally, Strict Day enforces device-level application blocking through Android's `DevicePolicyManager` (Device Owner mode) and verifies task completion via tamper-proof, server-side rule evaluation running on Supabase Edge Functions.

The client reports hardware capabilities honestly (`SUPPORTED`, `REQUIRES_DEVICE_OWNER`, `REQUIRES_USER_PERMISSION`), degrading securely rather than falsifying pass marks.

---

## System Architecture

```text
  [ Android Client (minSdk 26 / targetSdk 35) ]
         │
         ├── [ UI Presentation Layer ]
         │      - Jetpack Compose + Material 3 Navigation
         │      - Task Editor, Night Planner, Analytics, Active Lock Screen
         │
         ├── [ Enforcement Engine ]
         │      - DevicePolicyManager (Device Owner API)
         │      - Background App Whitelist / Blacklist Policy Enforcement
         │      - BootReceiver + WorkManager Daemon Resumption
         │
         ├── [ Persistence Layer ]
         │      - Room Database (SQLCipher / encrypted-storage)
         │      - DataStore Preferences for runtime state
         │
         │  TLS 1.3 Normalized Verification Events (Append-Only)
         ▼
  [ Supabase Server Infrastructure ]
         │
         ├── [ verify-task Edge Function ]
         │      - Server-side rule evaluator
         │      - Verification status generation (append-only audit log)
         │
         └── [ PostgreSQL Database with Row-Level Security (RLS) ]
                - Device policy state mirroring
                - Multi-tenant tenant segregation
```

---

## Technical Specifications

- **Language & Compiler:** Kotlin 2.1.0, Android Gradle Plugin (AGP) 8.7.3, Gradle 8.11.1.
- **Android Target:** minSdk 26 (Android 8.0 Oreo), targetSdk 35 (Android 15).
- **UI Architecture:** Jetpack Compose with Material 3 design tokens and unidirectional data flow (MVI / MVVM).
- **Dependency Injection:** Dagger Hilt with `HiltWorkerFactory` for background task scheduling.
- **Background Dispatcher:** Android WorkManager (`@HiltWorker`) with automatic device boot persistence.
- **Security & Cryptography:** AndroidX `security-crypto` (EncryptedSharedPreferences and MasterKey AES-GCM).
- **Backend & Cloud Sync:** Supabase Edge Functions (Deno / TypeScript) and PostgreSQL with strict Row-Level Security.
- **Test Coverage:** 29 automated unit tests covering constraint satisfaction, schedule validation, and edge rule evaluation.

---

## Server-Authoritative Honesty Contract

1. **Zero Client-Side Verification:** The Android device only generates and uploads normalized evidence payloads (`verification_events`). The decision to unlock a device or mark a milestone passed is evaluated exclusively on the server.
2. **Honest Capability Reporting:** The system queries Android subsystem capabilities at runtime. If Device Owner permissions are missing, the app explicitly reports `REQUIRES_DEVICE_OWNER` rather than simulating a fake lock screen.
3. **Append-Only Auditing:** Every policy change, lock engagement, and verification attempt is permanently logged to an append-only audit trail in PostgreSQL.

---

## Building & Verification

### Prerequisites
- JDK 17
- Android SDK 35 (Platform Tools, Build Tools 35.0.0)

```bash
# Configure Android environment
export JAVA_HOME=/path/to/jdk17
export ANDROID_HOME=/path/to/Android/Sdk

# Run test suite and compile debug APK
./gradlew testDebugUnitTest
./gradlew assembleDebug
```

The resulting package is compiled to `app/build/outputs/apk/debug/app-debug.apk`.

---

## Authorship & Intellectual Property

- **Lead Systems Architect:** Mullainathan
- **Email:** mullainathan95@gmail.com
- **Organization:** Brix Softworks
- **License:** Proprietary - All rights reserved by Mullainathan
