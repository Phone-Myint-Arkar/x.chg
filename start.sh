#!/bin/bash
source venv/bin/activate
python app.py &
sleep 2
open index.html
