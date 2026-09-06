\# Serving setup for `bench\_log.csv`



\## Model: FLM-4B-Instruct (dense)



| property | value |

|---|---|

| parameters | 4.2 B |

| layers | 28 |

| d\_model | 3072 |

| attention heads (Q) | 24 |

| KV heads (GQA) | 8 |

| head\_dim | 128 |

| vocab | 128k |

| weights precision | fp16 |

| KV cache precision | fp16 |



\## Hardware \& serving config



| property | value |

|---|---|

| GPU | 1× NVIDIA L4 (24 GB) |

| memory bandwidth (peak) | 300 GB/s |

| fp16 dense compute (peak) | \~121 TFLOPS |

| `max\_model\_len` | 4096 |

| `gpu\_memory\_utilization` | 0.92 |

| non-KV runtime overhead (activations, CUDA graphs, etc.) | assume \~1.6 GB |



\## How the load test was run



Each row of `bench\_log.csv` is one run: `num\_requests` identical requests

submitted simultaneously with the given `prompt\_len` and `gen\_len`

(all requests generate exactly `gen\_len` tokens, no early stopping).



Column notes:



\- `reported\_tok\_s` — the harness's built-in throughput counter

\- `ttft\_ms\_p50` — median time to first token

\- `itl\_ms\_p50` — median inter-token latency during decode

\- `e2e\_ms\_p95` — p95 end-to-end request latency

\- `preempted\_seqs` — sequences the scheduler preempted at least once

\- `kv\_cache\_util` — peak KV cache block utilization

