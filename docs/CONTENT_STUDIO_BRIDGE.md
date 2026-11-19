# Content Studio bridge (offline pilot)

The engine reuses Casa Viva's existing save contract rather than inventing a new writer. Reference: `wordpress/casa-viva-dropship-core/includes/class-cvd-content-studio.php` in Casa-Viva (main c1bfdf).

1. Read canonical WooCommerce `context=edit`, verifying tenant, numeric ID and SKU.
2. Read Studio `/wp-json/casa-viva/v1/contenido/products?filtro=all&id=ID` (the presence of `filtro` selects v2). Projection has no SKU; identity is checked by Woo and numeric ID.
3. Require a current local human approval and matching text, publication status, and ordered gallery in both reads. Require Studio's SHA-256 version and complete seven-field brief. Unknown/partial briefs block; matrix keys are omitted because the server preserves them.
4. Compile an offline descriptor for `/wp-json/casa-viva/v1/contenido/save`, with `id`, `version`, all three text fields and all seven brief fields. Never send `action=publish`. No HTTP sender exists. Already published products would change live even without that action.
5. Reverse only against fresh canonical and Studio reads matching the approved after-text and use the new server version. No automatic restoration of media, status or other metadata is implied.

Studio has an atomic per-product lock shared with its own requests and checks its version, but this is not a global lock against unrelated wp-admin edits. The endpoint sanitizes text and brief, sets editorial ownership, updates ready/lock metadata and keeps ten history entries. Text-only reversal is not a full database rollback. A real staging roundtrip must certify sanitization, exact text restoration, preservation of brief/gallery and metadata side effects before enabling any write path. MK- products reject a proposed short-text change because Studio preserves their canonical notice.

No credentials, production POST, media upload or additional spending. The local approval actor is not an authenticated Studio approver; production authorization remains a separate gate.

## Acceptance of the controlled roundtrip

`studio_roundtrip.verify_roundtrip` accepts three independently acquired pairs of canonical Woo and Studio reads (before, after, restored). It checks the exact approved text in both directions, status, type, ordered attachment IDs, price fields, stock fields, full brief including matrix, and Studio version transition A → B → A. Missing protected evidence or any deviation rejects the roundtrip. It does not authenticate the provenance of snapshots, attest a server run, or authorize a request.

Before enabling a writer, use an already authorized isolated staging clone, confirm no production synchronization, obtain a fresh backup and authenticated editorial approval, capture the before values including editorial metadata, execute the forward request once, re-read, then reverse once and re-read. Record server response codes, timestamps and non-text metadata changes separately; never record credentials. If the response is lost, read again rather than retry blindly. Require exact protected-field equality and explicitly account for editorial ownership, ready flag, fixed text timestamp and history changes. Stop on conflict. No staging runtime is installed in the current development workspace, so local tests are synthetic and the KM-3018 server roundtrip remains pending. Do not treat the public snapshot or editor backup as `woo_rest_edit`.
