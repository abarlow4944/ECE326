## Lab 2: Preliminary Benchmark Results
- Maximum number of connections that can be handled before connection drops: 26
- Maximum number of requests per second that can be sustained by the server when operating with maximum number of connections: 181
- Average and 99 percentile of response time:
    - Time per request: 143.700 ms (mean)
    - Time per request: 5.527 ms (mean, across all concurrent requests)
    - 99 percentile: 433 ms
- Utilization when max performance is sustained:
    - CPU: 99.67% idle
    - Memory: 420MB used
    - Disk IO: bi: 52 blocks/s bo: 1967 blocks/s
    - Network: recv: 341KB/s, send: 83KB/s

## Lab 3: Preliminary Benchmark Results
- Maximum number of connections that can be handled before connection drops: 26
- Maximum number of requests per second that can be sustained by the server when operating with maximum number of connections: 208
- Average and 99 percentile of response time:
    - Time per request: 124.814 ms (mean)
    - Time per request: 4.801 ms (mean, across all concurrent requests)
    - 99 percentile: 1126 ms
- Utilization when max performance is sustained:
    - CPU: 99.67% idle
    - Memory: 392MB used
    - Disk IO: bi: 183 blocks/s bo: 89 blocks/s
    - Network: recv: 427KB/s, send: 90KB/s 

Compared with Lab 2, the Lab 3 search engine maintained a similar maximum connection capacity (26 concurrent clients) but achieved a slightly higher maximum throughput of 208 requests per second versus 181 in Lab 2. The mean response time also improved from 143.7 ms to 124.8 ms, although the 99th-percentile latency increased significantly (from 433 ms to 1126 ms), indicating greater variability under heavy load. System utilization remained mostly unchanged, with CPU usage still roughly 99 % idle. Memory usage decreased slightly, while disk I/O patterns shifted due to the introduction of SQLite queries and database reads instead of purely static content. Overall, Lab 3 demonstrates improved average performance but less predictable tail latency. This could be because of database access overhead and PageRank-based result sorting.
