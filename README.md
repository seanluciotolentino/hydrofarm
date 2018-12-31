hydrofarm
==========

This is the codebase for my hydroponic farm pet project. Two raspberry pis run on crontabs to (1) collect data from sensors (light, moisture, temperature - `sensors.py`) and (2) operate servos and a webcam to capture plant growth over time (`camera.py`). 

Additionally I've repurposed an old laptop to act as a backend file server (`server.py`) and frontend user interface for data (`dashboard`).
