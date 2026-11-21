# Answer key: Insurance Policy

Document: `sample_insurance_policy.txt` (fake sample). Keep this file away from the AI.

## What the page should show

**Expected: 5 high risk · 3 watch out · 1 minor note**

**Must catch as High risk: clauses 3, 4, 5, 6 and 8**

| Clause | Title | Expected | Got | Pass? |
|---|---|---|---|---|
| 1 | Coverage | Minor note |  |  |
| 2 | Premium | Watch out |  |  |
| 3 | Deductible | High risk |  |  |
| 4 | Exclusions | High risk |  |  |
| 5 | Claim Deadline | High risk |  |  |
| 6 | Cancellation by You | High risk |  |  |
| 7 | Cancellation by Us | Watch out |  |  |
| 8 | Renewal | High risk |  |  |
| 9 | Disputes | Watch out |  |  |

## Clause by clause

### Clause 1: Coverage → **Minor note** (other)

**What it says:** "We insure your dwelling against fire, theft and storm damage up to $250,000."

**Why:** Says what is covered and up to how much. Normal.

### Clause 2: Premium → **Watch out** (hidden fees)

**What it says:** "Your premium is $90 per month. We may increase the premium at any renewal without prior notice."

**Why:** The price can go up at renewal without telling you first.

### Clause 3: Deductible → **High risk** (hidden fees)

**What it says:** "You pay the first $2,500 of every claim. For wind or hail damage the deductible is 5% of the insured amount."

**Why:** For wind or hail you pay 5% of $250,000, which is about $12,500, before they pay anything.

### Clause 4: Exclusions → **High risk** (other)

**What it says:** "We do not cover flood, earth movement, mold, or damage caused by lack of maintenance, as decided by us."

**Why:** Many common damages are not covered, and "as decided by us" lets them choose.

### Clause 5: Claim Deadline → **High risk** (other)

**What it says:** "You must report any loss within 14 days. Claims reported later may be denied in full."

**Why:** Report a loss later than 14 days and they can refuse the whole claim.

### Clause 6: Cancellation by You → **High risk** (cancellation)

**What it says:** "If you cancel during the policy year, you must pay a cancellation fee of $150 and no premium is refunded for the current month."

**Why:** Cancelling costs $150, and you lose the money for the current month.

### Clause 7: Cancellation by Us → **Watch out** (cancellation)

**What it says:** "We may cancel this policy at any time by mailing a notice 10 days in advance."

**Why:** They can cancel your cover with only 10 days' notice.

### Clause 8: Renewal → **High risk** (auto-renewal)

**What it says:** "This policy renews automatically each year unless you give written notice 60 days before the renewal date."

**Why:** It renews by itself every year unless you write 60 days before.

### Clause 9: Disputes → **Watch out** (liability)

**What it says:** "Any dispute must be settled by binding arbitration. You waive your right to a jury trial."

**Why:** You cannot go to court with a jury. A private arbitrator decides.

## How to judge

- **Pass:** every Must catch clause shows **High risk**.
- **Fine:** a Watch out shown as Minor note (or the other way round) for one or two clauses.
- **Fail:** a Must catch clause shows Watch out or Minor note, or a clause is missing.
- **Also check:** each plain-English explanation keeps the same amounts, dates and deadlines as "What it says".
