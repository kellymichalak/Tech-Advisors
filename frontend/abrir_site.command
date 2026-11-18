#!/bin/bash
cd "$(dirname "$0")"
open "http://localhost:8080/pages/resumos.html"
python3 -m http.server 8080
