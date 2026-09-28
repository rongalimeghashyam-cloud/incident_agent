# Run frontend (Windows PowerShell)
cd frontend
if (-not (Test-Path -Path node_modules)) {
    npm install
}
npm run dev
