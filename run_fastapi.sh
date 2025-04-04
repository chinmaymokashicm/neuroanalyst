# ! Do not run this script - this is only for reading

cd $HOME/github/neuroanalyst
source venv/bin/activate
uvicorn fast:app --port 3000