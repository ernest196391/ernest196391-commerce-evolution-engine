# Offline daily worker

Connects CatalogQueue and supervisor. Content-addressed input JSON and gallery PNG snapshots are persisted before enqueue; SHA256 verified on read, report saved before lease completion; retries are safe and results immutable by content hash. Source references are recorded, not independent verification of original provenance. Store root on durable local disk; never commit it or share it publicly. No remote calls, no paid API, no publish. Commands:

```
python -m src.commerce_evolution_engine.catalog_worker --root /persistent/catalog-state submit --product product.json --research research.json --draft draft.json --photos gallery
python -m src.commerce_evolution_engine.catalog_worker --root /persistent/catalog-state run --tenant casa-viva --daily-limit 10
python -m src.commerce_evolution_engine.catalog_worker --root /persistent/catalog-state status --tenant casa-viva
```

Run processes prepared candidates only; it does not yet research or generate images autonomously. Inputs changed => new job. Local real pilot run: 6557 KM-3018 awaiting_review; nx-132-1 KM-9013 awaiting_review; MK-2837 Sankey blocked. Re-run returned empty array. 26 local unit tests passed; three new tests verify restart/idempotency, immutable snapshots, changed image fingerprint and tamper rejection. No deployment/scheduler installed; next approval ledger binding input and result hashes, then guarded WooCommerce staging and rollback. Rollback code by reverting commit; retain state for audit. Do not launch supplier/inventory modules.
