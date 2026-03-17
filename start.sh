#!/usr/bin/env bash

set -eu

pip install -q -r requirements.txt

streamlit run app.py --server.port=8501 --server.address=0.0.0.0
