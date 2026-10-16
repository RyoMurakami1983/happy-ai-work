# Consumer and independent title formatting

DESIGN.md authorizes consumer implementation only against the verified provider/api.yaml artifact. Its required checksum is retained in plan.md. The provider artifact is absent; its API must not be invented.
The independent formatting.title(value) behavior strips leading/trailing whitespace while preserving all interior text. That local behavior has no provider dependency.
