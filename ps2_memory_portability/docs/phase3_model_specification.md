# Phase 3 model specification

This document extends the verified Phase 2 Bayesian portability game into a
single computational research story. All new values are normalized benchmark
assumptions, not empirical estimates.

## Social Choice

### Stakeholders and alternatives

The stakeholders are Platform A, Platform B, and users. Realized collective
alternatives are `(P,P)`, `(P,L)`, `(L,P)`, and `(L,L)`. Ex-ante comparisons
use complete Bayesian strategy profiles such as `(LL,LL)`, `(PL,PL)`, and
`(PP,PP)`. A realized action outcome and a type-contingent Bayesian strategy
profile are not the same object.

### Collective objective

Phase 2 platform payoffs are unchanged. The binary user-mobility component is

\[
U_{user}(P,P)=m,\qquad U_{user}(P,L)=U_{user}(L,P)=U_{user}(L,L)=0,
\]

where `m >= 0` is normalized. Mutual adoption is required for the full modeled
interoperability benefit. Unilateral portability may matter in reality, but it
is deliberately outside this initial benchmark.

The normalized utilitarian objective is

\[
W=u_A+u_B+U_{user}.
\]

Cardinal comparability is an explicit modeling assumption. The `m` sensitivity
analysis exposes how this normalization affects the calculation rather than
presenting it as an observed consumer valuation.

### Expected welfare

For a complete profile `(s_A,s_B)`, the implementation enumerates low-low,
low-high, high-low, and high-high states under independent types. In each state
it calls the Phase 2 payoff function, adds the user component, and weights the
result by the state probability.

At `c_L=0.2`, `c_H=1.2`, and `p=0.7`:

- `(LL,LL)`: platform welfare `0`, user welfare `0`, so `W=0`.
- `(PL,PL)`: platform welfare `1.68`, user welfare `0.49m`, so
  `W=1.68+0.49m`.
- `(PP,PP)`: platform welfare `3`, user welfare `m`, so `W=3+m`.

On `m=0.0,0.1,...,4.0`, the ranking is always `PP > PL > LL`. This is a
collective comparison only: `(PP,PP)` is not a Phase 2 pure BNE at the
benchmark, while `(LL,LL)` and `(PL,PL)` are.

## Mechanism Design

### Verified portability incentive

The reduced-form parameter `tau >= 0` is a verified portability incentive. It
may represent certification, access to an interoperability ecosystem, a
compliance credit, or another verified benefit. The model does not specify its
financing and does not treat it as a literal cash subsidy.

Portable actions receive `tau`; Locked actions do not. Therefore

\[
EU_\tau(P\mid c)=3q-1-c+\tau,\qquad EU_\tau(L\mid c)=q,
\]

and Portable is a weak best response iff

\[
2q-1-c+\tau\ge 0.
\]

The Phase 2 result is reproduced exactly at `tau=0`.

### PL thresholds

For symmetric `PL`, the low-type constraint is

\[
p\ge\frac{1+c_L-\tau}{2},
\]

or `tau_min=max(0,1+c_L-2p)`. The high type must also remain willing to
choose Locked, which requires

\[
\tau\le 1+c_H-2p.
\]

The full enumerator checks both constraints rather than applying only the lower
threshold. At `p=0.4`, the low-type boundary is `tau=0.4`; `PL` is absent at
`0.39` and is a weak pure BNE at `0.40`. At `p=0.7`, `PL` already exists at
`tau=0` and remains a weak pure BNE through its high-type boundary `tau=0.8`.
Immediately above `0.8`, the high type no longer prefers Locked in that
profile.

### Lock-in thresholds and interpretation

Against `LL`, the low type is indifferent at `tau=1+c_L=1.2` and the high type
at `tau=1+c_H=2.2`. Because BNE uses weak best responses, `(LL,LL)` remains a
pure BNE at exactly `tau=1.2` but disappears immediately above it. Thus a
moderate incentive can expand portability equilibria while retaining lock-in.
The mechanism changes the equilibrium correspondence without automatically
selecting a unique outcome.

The 99-by-51 `(p,tau)` grid evaluates all 16 profiles at each point. It also
shows that `(PP,PP)` can become sustainable at moderate incentives because a
high-cost type's incentive depends on the rival's portability probability. At
the benchmark costs, `(PP,PP)` first appears weakly at `tau=c_H-1=0.2`.
No welfare-optimal `tau` is claimed because financing and implementation costs
of the incentive are not modeled.

## Auction

### Allocation environment

- **Scarce resource:** one user's primary AI-assistant slot for the next service
  period.
- **Participants:** Platform A and Platform B.
- **Values:** independent normalized private values `v_i ~ Uniform(0,1)`.
- **Information:** each platform observes only its own value; the distribution,
  mechanism, and reserve are common knowledge.
- **Bids:** one sealed bid per platform.
- **Reserve:** the user's normalized switching hurdle, `r_locked=0.5` or
  `r_portable=0.2`.
- **Allocation:** the highest eligible bid wins; no allocation occurs if neither
  bid reaches `r`.
- **Tie-breaking:** Platform A wins an exact eligible tie.
- **Stopping rule:** collect one bid from each platform, apply the reserve,
  allocate at most one slot, compute the payment, and terminate.

The switching hurdle belongs to the user and enters as a reserve rather than
being mechanically subtracted from a platform's value.

### First-price mechanism

The winner pays/offers its own bid. For two symmetric risk-neutral bidders with
iid Uniform(0,1) values, participating types use

\[
b_{FPA}(v;r)=\frac{v^2+r^2}{2v}=\frac v2+\frac{r^2}{2v},\qquad v\ge r.
\]

Types below `r` submit no eligible bid. At `v=r`, the bid equals `r`.

### Second-price mechanism

Truthful bidding `b(v)=v` is the benchmark dominant strategy. The highest bid
wins if it reaches the reserve, and the payment is the larger of the reserve
and the second-highest bid.

### Metrics and validation

The simulation records valuations, bids, allocation, winner, payment, winner
value, winner utility, user compensation, and whether the highest-value
platform won. With two iid Uniform values,

\[
Pr(\text{allocation})=1-r^2.
\]

The analytical benchmarks are `0.75` under lock-in and `0.96` under
portability. Conditional allocative efficiency means that the highest-value
eligible platform receives the slot. Payment is reported both conditional and
unconditional on allocation. No additional total-surplus formula is imposed,
because doing so would require a further assumption about how the reserve maps
into user utility or cost.

### Boundary

The user is not literally sold. The primary-assistant slot is a stylized
allocation abstraction, and all values and reserves are normalized. See
`auction_boundary.md` for the complete interpretation boundary.
