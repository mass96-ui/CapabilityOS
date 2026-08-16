# CapabilityOS Web Frontend Dockerfile
# Builds and serves the Next.js learner application
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
WORKDIR /app

FROM base AS deps
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json ./apps/web/package.json
COPY apps/admin/package.json ./apps/admin/package.json
COPY packages/ui/package.json ./packages/ui/package.json
COPY packages/types/package.json ./packages/types/package.json
COPY apps/web ./apps/web
COPY apps/admin ./apps/admin
COPY packages/ui ./packages/ui
COPY packages/types ./packages/types
RUN pnpm install --frozen-lockfile --ignore-scripts

FROM base AS build
COPY . .
RUN pnpm build

FROM node:20-alpine AS runtime
WORKDIR /app
COPY --from=build /app /app
CMD ["sh", "-c", "pnpm --dir apps/web dev"]
