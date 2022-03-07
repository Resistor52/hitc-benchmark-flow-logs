# Head in the Clouds - Benchmark Flow Logs Script

This is the Companion Repository for **Head in the Clouds** [Episode 18 - Benchmark AWS Flow Logs](https://headintheclouds.site/episodes/episode18). Refer to the [show notes](https://headintheclouds.site/episodes/episode18) or [YouTube Video](https://www.youtube.com/watch?v=AmN-1LKPhP0) for a detailed discussion of these scripts.

The repository consists of two python scripts:

* **generate-test-traffic.py** - This script generates TCP traffic such that the source port is a timestamp that can be used to benchmark a remote flow logging system.
* **plotObservations.py** - This script uses MatPlotLib to generate plots to visualize the results of the CloudWatch Logs Insights  query discussed in Head in the Clouds EP18


**NOTE:** This repo has two branches - the main branch may be updated over time while the `hitc-ep18` branch is locked so that the scripts are left "as-is" to match the discussion in the YouTube Video. There is a known issue in `generate-test-traffic.py` where it fails to send a packet approx. every 192 seconds. _Eventually_ this will be fixed in the main branch. 
