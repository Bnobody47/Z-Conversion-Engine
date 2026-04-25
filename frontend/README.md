# Frontend Demo (Next.js)

Interactive Next.js dashboard for full end-to-end demo testing with buttons and clear per-step outputs.

## Start backend

From repo root:

```powershell
uvicorn agent.main:app --host 0.0.0.0 --port 8010
```

## Start frontend

From `frontend/`:

```powershell
npm install
npm run dev
```

Open: `http://127.0.0.1:3000`

## Demo features

- Run the full flow with one click (`Run Full Flow`)
- Run each test step individually with dedicated buttons
- See each result in a separate card (status + JSON body)
- Load and display `docs/final_smoke_test_output.json` from an internal API route
