# Answer key: Gym Membership

Document: `sample_gym_membership.txt` (fake sample). Keep this file away from the AI.

## What the page should show

**Expected: 4 high risk · 3 watch out · 2 minor note**

**Must catch as High risk: clauses 3, 4, 5 and 8**

| Clause | Title | Expected | Got | Pass? |
|---|---|---|---|---|
| 1 | Membership | Minor note |  |  |
| 2 | Joining Fee | Watch out |  |  |
| 3 | Annual Fee | High risk |  |  |
| 4 | Automatic Renewal | High risk |  |  |
| 5 | Early Cancellation | High risk |  |  |
| 6 | Price Changes | Watch out |  |  |
| 7 | Freezing | Watch out |  |  |
| 8 | Injuries | High risk |  |  |
| 9 | Guests | Minor note |  |  |

## Clause by clause

### Clause 1: Membership → **Minor note** (other)

**What it says:** "You get access to the gym during opening hours for 12 months at $35 per month."

**Why:** The basic price and length. Normal.

### Clause 2: Joining Fee → **Watch out** (hidden fees)

**What it says:** "A one-time joining fee of $99 is charged on signup and is not refundable."

**Why:** A $99 fee at the start that you cannot get back.

### Clause 3: Annual Fee → **High risk** (hidden fees)

**What it says:** "An annual maintenance fee of $59 is billed in month 6 of every year."

**Why:** An extra $59 every year, charged in month 6, which is easy to miss.

### Clause 4: Automatic Renewal → **High risk** (auto-renewal)

**What it says:** "After 12 months the membership continues month to month. Cancelling requires a signed letter sent by registered mail 30 days before the next billing date."

**Why:** It keeps going every month, and you can only stop it by registered mail, 30 days ahead.

### Clause 5: Early Cancellation → **High risk** (cancellation)

**What it says:** "If you cancel before the 12 months end, you owe 50% of the remaining monthly fees."

**Why:** Leaving early costs half of all the months you have left.

### Clause 6: Price Changes → **Watch out** (hidden fees)

**What it says:** "We may raise the monthly fee with 7 days' notice posted on our notice board."

**Why:** The price can rise with only 7 days' notice on a board at the gym.

### Clause 7: Freezing → **Watch out** (hidden fees)

**What it says:** "You may freeze your membership for up to 3 months for a $20 monthly freeze fee."

**Why:** Pausing your membership still costs $20 a month.

### Clause 8: Injuries → **High risk** (liability)

**What it says:** "You use the gym at your own risk. The gym is not responsible for any injury, even if caused by faulty equipment."

**Why:** The gym is not responsible even if broken equipment hurts you.

### Clause 9: Guests → **Minor note** (other)

**What it says:** "Each member may bring one guest per month at no charge."

**Why:** A free guest pass. Good for you.

## How to judge

- **Pass:** every Must catch clause shows **High risk**.
- **Fine:** a Watch out shown as Minor note (or the other way round) for one or two clauses.
- **Fail:** a Must catch clause shows Watch out or Minor note, or a clause is missing.
- **Also check:** each plain-English explanation keeps the same amounts, dates and deadlines as "What it says".
