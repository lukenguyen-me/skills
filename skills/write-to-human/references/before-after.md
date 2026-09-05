# Before and after

Use these as a voice model. Keep every fact. Change the shape.

The names below are generic. Replace them with the names of the current project when you write a real reply.

## Status after a change

**Before (code-first, long, passive):**

> I refactored `orderRepo.complete()` to persist through a local outbox with exponential backoff, so the mutation is no longer a synchronous cloud insert. Quota errors are retried after a compaction pass.

**After (outcome, then example):**

> An order can now finish when the internet is down. The device stores the order and sends it when the connection returns.
>
> Example: a clerk closes a sale at 16:00 with no Wi-Fi. The order still completes on the counter tablet. It uploads when the shop router is back.

## A complex problem

**Before (abstract, no scene):**

> The two devices can diverge because writes are accepted locally and the cloud is eventually consistent, so a later read may not observe the earlier write until sync completes.

**After (claim, then example):**

> Two devices can show different data until both have sent their changes to the cloud.
>
> Example: the front desk checks a customer in at 09:02. The back-office screen still shows "not arrived" until it receives that check-in. After sync, both screens show the same customer.

## An instruction

**Before (hedged, two actions, missing actor):**

> After having been initiated, the process should be monitored to ensure that any potential issues can be identified and addressed in a timely manner.

**After:**

> Start the process.
> Watch the process.
> If a problem occurs, fix it immediately.

## A report of what you did

**Before:**

> Wired up the new row-level policy on `orders` and added a covering index on `(organization_id, started_at)` which should make the owner overview snappier.

**After:**

> The owner overview now loads this location's orders faster. Staff from one location cannot read another location's orders.
>
> No action needed from you.

## A planning reply

**Before:**

> We should extract a retry queue behind the repository, add idempotency keys, and gate the new path on a feature flag before touching the UI.

**After:**

> The plan is: a sale can finish when the network drops, without a duplicate charge if the clerk taps Pay twice.
>
> Example: the clerk taps Pay, the Wi-Fi dies, and they tap Pay again. The customer is charged once. The second tap does not create a second order.
>
> I can show the implementation options if you want them.

## A bug diagnosis reply

**Before:**

> The race is in the outbox flush: two tabs both see `pending` and both POST, so the unique constraint on `external_id` 409s and the UI stays on "saving".

**After:**

> Two open tabs can send the same order twice. The second send fails. The screen stays on "saving", so the clerk thinks the sale did not complete.
>
> Example: a clerk has the register open on the counter tablet and on a phone. Both send the 14:10 order. One succeeds. The other fails. The phone still shows "saving".
>
> The sale is usually already in the cloud. The next step is to stop the double send.

## When the human asked for the code

Keep the outcome first. Then give the detail they asked for.

> Orders can finish offline. Pending orders stay on the device until the cloud accepts them.
>
> The write path is the storage layer → local outbox → cloud. I can show the diff if you want it.
