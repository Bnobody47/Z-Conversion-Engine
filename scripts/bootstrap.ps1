python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r .\agent\requirements.txt
python .\agent\seed_demo_data.py
python .\eval\run_tau2_baseline.py
Write-Output "Bootstrap complete."
