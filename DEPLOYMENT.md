# Deployment

InsightForge AI deploys as three services:

- BI Copilot API on Render
- Data Sentinel API on Render
- React/Vite frontend on Vercel

## Render

Use the root `render.yaml` Blueprint.

1. Push this repository to GitHub.
2. In Render, create a new Blueprint from the repository.
3. Use the repository root for the Blueprint file.
4. Set these environment variables:

```env
GEMINI_API_KEY=your-real-gemini-key
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

Render will create:

- `insightforge-bi-copilot-api`
- `insightforge-data-sentinel-api`

After deploy, copy both Render service URLs.

## Vercel

Create a Vercel project from the same repository.

Use these settings:

```text
Root Directory: bi-copilot/frontend
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
```

Set these environment variables in Vercel:

```env
VITE_API_BASE_URL=https://your-bi-copilot-api.onrender.com
VITE_SENTINEL_API_BASE_URL=https://your-data-sentinel-api.onrender.com
```

Redeploy Vercel after setting the variables.

## Final Checks

- Open the Vercel URL.
- The Overview page should show both APIs as online.
- Test BI Copilot with `Top products by revenue`.
- Test Data Sentinel with `10, 12, 11, 13, 100, 12, 11, 200, 9`.
