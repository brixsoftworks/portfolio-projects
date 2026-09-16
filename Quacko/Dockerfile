# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 0: dependencies (full repo, dev incl. — needed for expo export + esbuild)
# ---------------------------------------------------------------------------
FROM node:24-bookworm-slim AS deps
WORKDIR /repo
COPY package.json package-lock.json .npmrc ./
COPY apps apps
COPY packages packages
RUN npm ci

# ---------------------------------------------------------------------------
# Stage 1: build the website (Expo web export)
# ---------------------------------------------------------------------------
FROM deps AS web
WORKDIR /repo/apps/mobile
ENV EXPO_PUBLIC_DEMO_MODE=0 \
    EXPO_PUBLIC_API_URL= \
    CI=1
RUN npx expo export --platform web --output-dir /build/web

# ---------------------------------------------------------------------------
# Stage 2: build the server bundle (esbuild; better-sqlite3 stays external)
# ---------------------------------------------------------------------------
FROM deps AS server
WORKDIR /repo
RUN npm run build --workspace=@quacko/server

# ---------------------------------------------------------------------------
# Stage 3: runtime — pruned prod deps + bundled server + exported web
# ---------------------------------------------------------------------------
FROM node:24-bookworm-slim AS runtime
ENV NODE_ENV=production \
    PORT=8787 \
    HOST=0.0.0.0 \
    DATA_DIR=/data \
    WEB_DIR=/app/web
WORKDIR /app

COPY --from=server /repo/package.json /repo/package-lock.json /repo/.npmrc ./
COPY --from=server /repo/apps/server/package.json ./apps/server/package.json
# trustedDependencies in the root package.json lets npm build better-sqlite3
# non-interactively; --omit=dev keeps the runtime image lean.
RUN npm ci --omit=dev --workspace=@quacko/server

COPY --from=server /repo/apps/server/lib/index.cjs ./apps/server/lib/index.cjs
COPY --from=web /build/web ./web

VOLUME ["/data"]
EXPOSE 8787
CMD ["node", "apps/server/lib/index.cjs"]