# Serverless research notes

Serverless architectures can reduce the need to manage servers and can scale automatically with demand. Their cost model is often usage-based, which can suit workloads with variable traffic.

Potential tradeoffs include cold-start latency, execution limits, provider-specific services, and the need to understand distributed logs and tracing. Costs should be monitored because high request volume or inefficient functions can still become expensive.

Well-designed systems use least-privilege permissions, retries with limits, idempotent handlers, observability, and clear service boundaries. Architecture decisions depend on workload patterns, latency requirements, operational experience, and portability needs.
