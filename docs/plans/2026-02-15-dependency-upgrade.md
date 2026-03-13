# Dependency Upgrade Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade all outdated Python and npm dependencies, migrate frontend from react-scripts to Vite.

**Architecture:** Backend upgrades are in-place pip version bumps with test verification. Frontend migration replaces CRA toolchain with Vite, updates tsconfig, moves index.html, and converts env vars. Each phase commits independently for safe rollback.

**Tech Stack:** Python 3.12, FastAPI, Vite 6, React 19, TypeScript 5, Ant Design 5

---

### Task 1: Backend - Remove unused packages

**Files:**
- Modify: `backend/requirements.txt`

**Step 1: Edit requirements.txt**

Remove `pathlib2==2.3.7` (Python 3 has pathlib built-in) and delete the duplicate `python-multipart==0.0.6` line (appears on both line 5 and line 15).

Updated `backend/requirements.txt`:
```
# backend/requirements.txt
# FastAPI core
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0

# Auth
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Dev tools
python-dotenv==1.0.0

# Excel
pandas==2.1.4
openpyxl==3.1.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
```

**Step 2: Uninstall pathlib2**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && pip uninstall pathlib2 -y
```
Expected: `Successfully uninstalled pathlib2-2.3.7`

**Step 3: Verify nothing imports pathlib2**

Run:
```bash
grep -r "pathlib2" /home/ubuntu/shenyuan-erp/backend/app/ --include="*.py"
```
Expected: no output (nothing imports it)

**Step 4: Verify backend starts**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate && python -c "from app.main import app; print('OK')"
```
Expected: `OK`

**Step 5: Commit**

```bash
cd /home/ubuntu/shenyuan-erp
git add backend/requirements.txt
git commit -m "chore: remove pathlib2 and deduplicate python-multipart"
```

---

### Task 2: Backend - Upgrade Python packages

**Files:**
- Modify: `backend/requirements.txt`

**Step 1: Upgrade all packages**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate
pip install \
  "fastapi==0.129.0" \
  "uvicorn[standard]==0.40.0" \
  "sqlalchemy==2.0.46" \
  "pydantic==2.12.5" \
  "pydantic-settings==2.13.0" \
  "python-jose[cryptography]==3.5.0" \
  "pytest==8.4.2" \
  "pytest-asyncio==0.25.3" \
  "pandas==2.3.3" \
  "openpyxl==3.1.5" \
  "python-multipart==0.0.22" \
  "python-dotenv==1.2.1"
```
Expected: all packages install without errors

**Step 2: Verify backend starts**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate
python -c "from app.main import app; print('OK')"
```
Expected: `OK`

If there are deprecation warnings or import errors, fix them before proceeding.

**Step 3: Run tests**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate
python -m pytest tests/ --ignore=tests/disabled --ignore=tests/manual -v --tb=short 2>&1 | tail -20
```
Expected: all tests pass (44 passed, 0 failed)

**Step 4: Test login API**

Run:
```bash
# Restart server first
sudo kill $(sudo lsof -t -i:8000) 2>/dev/null; sleep 2
cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
sleep 5
curl -s -X POST http://localhost:8000/api/v1/auth/login -d "username=admin&password=admin123" | python3 -c "import sys,json; d=json.load(sys.stdin); print('Login:', 'OK' if 'user' in d else 'FAIL')"
```
Expected: `Login: OK`

**Step 5: Update requirements.txt with new versions**

Update `backend/requirements.txt`:
```
# backend/requirements.txt
# FastAPI core
fastapi==0.129.0
uvicorn[standard]==0.40.0
python-multipart==0.0.22

# Database
sqlalchemy==2.0.46
pydantic==2.12.5
pydantic-settings==2.13.0

# Auth
python-jose[cryptography]==3.5.0
passlib[bcrypt]==1.7.4

# Dev tools
python-dotenv==1.2.1

# Excel
pandas==2.3.3
openpyxl==3.1.5

# Testing
pytest==8.4.2
pytest-asyncio==0.25.3
```

**Step 6: Commit**

```bash
cd /home/ubuntu/shenyuan-erp
git add backend/requirements.txt
git commit -m "chore: upgrade all Python dependencies to latest stable versions

FastAPI 0.104.1 -> 0.129.0
uvicorn 0.24.0 -> 0.40.0
SQLAlchemy 2.0.23 -> 2.0.46
pydantic 2.5.0 -> 2.12.5
pytest 7.4.3 -> 8.4.2
pandas 2.1.4 -> 2.3.3"
```

---

### Task 3: Frontend - Migrate from react-scripts to Vite

**Files:**
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html` (moved from public/)
- Create: `frontend/src/vite-env.d.ts`
- Modify: `frontend/tsconfig.json`
- Modify: `frontend/package.json`
- Modify: `frontend/src/index.tsx` → `frontend/src/main.tsx`
- Modify: `frontend/src/config/api.ts`
- Modify: `frontend/.env`
- Modify: `frontend/.env.development`
- Modify: `frontend/.env.production`
- Delete: `frontend/src/reportWebVitals.ts`
- Delete: `frontend/src/react-app-env.d.ts` (if exists)
- Delete: `frontend/src/setupTests.ts` (if exists)

**Step 1: Stop frontend if running**

Run:
```bash
pkill -f "react-scripts" 2>/dev/null; pkill -f "node.*frontend" 2>/dev/null
```

**Step 2: Install Vite and plugins**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/frontend
npm install --save-dev vite @vitejs/plugin-react vite-tsconfig-paths
```

**Step 3: Create vite.config.ts**

Create file `frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
```

**Step 4: Move and update index.html**

Move `frontend/public/index.html` to `frontend/index.html` and update it:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="申源ERP系统" />
    <link rel="apple-touch-icon" href="/logo192.png" />
    <link rel="manifest" href="/manifest.json" />
    <title>申源ERP系统</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Key changes:
- `%PUBLIC_URL%` replaced with `/` (Vite serves public/ assets at root)
- Added `<script type="module" src="/src/main.tsx">` (Vite entry point)
- Removed old `public/index.html` (keep other public/ files like favicon)

**Step 5: Rename index.tsx to main.tsx and clean up**

Rename `frontend/src/index.tsx` to `frontend/src/main.tsx` with updated content:

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

Changes: removed `reportWebVitals` import and call.

**Step 6: Create vite-env.d.ts**

Create file `frontend/src/vite-env.d.ts`:
```typescript
/// <reference types="vite/client" />
```

**Step 7: Update tsconfig.json**

Update `frontend/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "types": ["vite/client"]
  },
  "include": ["src"]
}
```

Changes: `target` es5→ES2020, `module` esnext→ESNext, `moduleResolution` node→bundler, added `types: ["vite/client"]`.

**Step 8: Update environment variables**

Update `frontend/src/config/api.ts`:
```typescript
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```

Update `frontend/.env`:
```
HOST=0.0.0.0
PORT=3000
```

Update `frontend/.env.development`:
```
VITE_API_BASE_URL=http://18.218.95.233:8000
```

Update `frontend/.env.production`:
```
VITE_API_BASE_URL=http://18.218.95.233:8000
```

**Step 9: Update package.json scripts**

In `frontend/package.json`, update the scripts section and remove proxy:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "start": "vite"
  }
}
```

Remove the `"proxy": "http://localhost:8000"` line (proxy is now in vite.config.ts).

Remove from dependencies: `react-scripts`, `web-vitals`, `d3-scale`, `d3-shape`.

Remove from eslintConfig section (entire block - Vite doesn't need it).

Remove the browserslist section (Vite uses its own defaults).

**Step 10: Delete CRA-specific files**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/frontend
rm -f src/reportWebVitals.ts
rm -f src/react-app-env.d.ts
rm -f src/setupTests.ts
rm -f public/index.html
```

**Step 11: Uninstall react-scripts and unused packages**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/frontend
npm uninstall react-scripts web-vitals d3-scale d3-shape
```

**Step 12: Install dependencies**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/frontend
npm install
```

**Step 13: Test Vite dev server**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/frontend
npx vite --host 0.0.0.0 --port 3000 &
sleep 5
curl -s http://localhost:3000 | head -5
```
Expected: HTML output with `<div id="root">` and `<script type="module"`

Kill dev server after test:
```bash
pkill -f "vite" 2>/dev/null
```

**Step 14: Test Vite build**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/frontend
npx tsc --noEmit 2>&1 | head -20
npx vite build 2>&1 | tail -10
```
Expected: TypeScript check passes, build creates `dist/` directory.

If there are TypeScript errors, fix them before committing.

**Step 15: Commit**

```bash
cd /home/ubuntu/shenyuan-erp
git add -A frontend/
git commit -m "feat: migrate frontend from react-scripts to Vite

- Replace CRA with Vite 6 for faster builds and dev server
- Move index.html to project root (Vite convention)
- Rename index.tsx to main.tsx
- Convert REACT_APP_* env vars to VITE_*
- Configure API proxy in vite.config.ts
- Remove web-vitals, d3-scale, d3-shape (unused)
- Remove reportWebVitals.ts and CRA boilerplate"
```

---

### Task 4: Frontend - Upgrade TypeScript and other dependencies

**Files:**
- Modify: `frontend/package.json`

**Step 1: Upgrade TypeScript to 5.x**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/frontend
npm install typescript@~5.7
```

**Step 2: Upgrade other dependencies**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/frontend
npm install antd@latest @ant-design/icons@latest react-router-dom@latest axios@latest
npm install --save-dev @types/node@latest @types/jest@latest
```

**Step 3: Verify TypeScript compilation**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/frontend
npx tsc --noEmit 2>&1 | head -30
```
Expected: no errors (or only warnings)

Fix any TypeScript errors that appear from the upgrade.

**Step 4: Verify Vite build**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/frontend
npx vite build 2>&1 | tail -10
```
Expected: build succeeds, output in `dist/`

**Step 5: Commit**

```bash
cd /home/ubuntu/shenyuan-erp
git add frontend/package.json frontend/package-lock.json
git commit -m "chore: upgrade TypeScript 4.9->5.7, antd, axios, react-router-dom"
```

---

### Task 5: Update startup scripts for Vite

**Files:**
- Modify: `scripts/start-erp-dev.sh`
- Modify: `scripts/start-erp-prod.sh`

**Step 1: Update dev script**

In `scripts/start-erp-dev.sh`, replace the frontend section (lines 28-41):

Replace:
```bash
echo "   启动React开发服务器..."
export HOST=0.0.0.0
export PORT=3000
export REACT_APP_API_BASE_URL=http://localhost:8000
nohup npm start > frontend.log 2>&1 &
```

With:
```bash
echo "   启动Vite开发服务器..."
nohup npx vite --host 0.0.0.0 --port 3000 > frontend.log 2>&1 &
```

**Step 2: Update prod script**

In `scripts/start-erp-prod.sh`, replace the frontend build/serve section (lines 35-44):

Replace:
```bash
echo "   构建生产版本..."
npm run build
echo "   使用serve启动生产服务器..."
# 先安装serve如果没有
if ! command -v serve &> /dev/null; then
    npm install -g serve
fi
export HOST=0.0.0.0
export REACT_APP_API_BASE_URL=http://18.218.95.233:8000
nohup /home/ubuntu/.npm-global/bin/serve -s build -l tcp://0.0.0.0:8080 > frontend.log 2>&1 &
```

With:
```bash
echo "   构建生产版本..."
npx vite build
echo "   使用serve启动生产服务器..."
if ! command -v serve &> /dev/null; then
    npm install -g serve
fi
nohup /home/ubuntu/.npm-global/bin/serve -s dist -l tcp://0.0.0.0:8080 > frontend.log 2>&1 &
```

Key change: `build` directory → `dist` directory (Vite default output).

**Step 3: Commit**

```bash
cd /home/ubuntu/shenyuan-erp
git add scripts/start-erp-dev.sh scripts/start-erp-prod.sh
git commit -m "chore: update startup scripts for Vite migration

- Dev: use 'npx vite' instead of 'npm start'
- Prod: use 'npx vite build' and serve 'dist/' instead of 'build/'"
```

---

### Task 6: Full system verification

**Step 1: Restart backend**

Run:
```bash
sudo kill $(sudo lsof -t -i:8000) 2>/dev/null; sleep 2
cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
sleep 5
curl -s http://localhost:8000/health | python3 -c "import sys,json; print(json.load(sys.stdin))"
```
Expected: `{'status': 'healthy', 'database': 'connected'}`

**Step 2: Start frontend dev server**

Run:
```bash
pkill -f vite 2>/dev/null; sleep 1
cd /home/ubuntu/shenyuan-erp/frontend
npx vite --host 0.0.0.0 --port 3000 &
sleep 5
curl -s http://localhost:3000 | grep -o '<div id="root">'
```
Expected: `<div id="root">`

**Step 3: Test API proxy**

Run:
```bash
curl -s -X POST http://localhost:3000/api/v1/auth/login -d "username=admin&password=admin123" | python3 -c "import sys,json; d=json.load(sys.stdin); print('Proxy login:', 'OK' if 'user' in d else 'FAIL')"
```
Expected: `Proxy login: OK`

**Step 4: Test production build**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/frontend
npx vite build
ls -la dist/index.html
```
Expected: `dist/index.html` file exists

**Step 5: Run backend tests**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate
python -m pytest tests/ --ignore=tests/disabled --ignore=tests/manual -v --tb=short 2>&1 | tail -5
```
Expected: all tests pass

**Step 6: Check final package versions**

Run:
```bash
cd /home/ubuntu/shenyuan-erp/backend && source venv/bin/activate
echo "=== Backend ==="
pip list 2>/dev/null | grep -iE "fastapi|uvicorn|sqlalchemy|pydantic|jose|pytest|pandas|openpyxl"
echo ""
echo "=== Frontend ==="
cd /home/ubuntu/shenyuan-erp/frontend
npx tsc --version
node -e "const p=require('./package.json'); console.log('antd:', p.dependencies.antd); console.log('vite:', p.devDependencies?.vite); console.log('typescript:', p.dependencies?.typescript || p.devDependencies?.typescript)"
```

**Step 7: Final commit if any fixes were needed**

```bash
cd /home/ubuntu/shenyuan-erp
git status
# If there are uncommitted fixes:
git add -A
git commit -m "fix: resolve compatibility issues from dependency upgrade"
```
