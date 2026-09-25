# Literature Review

This review supports the existing project, **Stay or Switch? Strategic Memory
Portability in Competing AI Assistants**. Citation keys refer to
[`references/references.bib`](../references/references.bib). “Memory portability”
is the project's stylized action; it is not treated as identical to every form
of compatibility, interoperability, or data portability studied below.

## 1. Switching Costs and Lock-In

Farrell and Klemperer survey how switching costs and network effects can bind
customers to vendors when products are incompatible. The resulting lock-in can
give a supplier ex post market power, change entry incentives, and magnify an
incumbent's advantage. Their central qualification matters here: competition
for customers before lock-in can sometimes be intense, so switching costs do
not mechanically weaken competition in every model or market
[@farrell2007coordination].

Klemperer's earlier overview isolates a related dynamic trade-off. A firm with
an installed customer base may balance a high price that harvests locked-in
customers against a low price that builds future market share
[@klemperer1995switching]. This is useful supporting context, but Farrell and
Klemperer provide the broader foundation used in the short paper. Neither
source studies AI assistants or estimates the value of portable AI memory.

## 2. Data Portability, Compatibility, and Platform Competition

Jeon, Menicucci, and Nasr are the closest strategic benchmark in this review.
They study two firms selling complementary products in a dynamic, two-period
setting. At the beginning of period one, firms simultaneously and
non-cooperatively choose compatibility or incompatibility; compatibility
requires both firms to choose it. Consumers may face switching costs in the
second period, and firms can price-discriminate using purchase histories. The
paper uses subgame-perfect Nash equilibrium (SPNE), not the static Bayesian
Nash equilibrium used in this project. It finds that sufficiently high
switching costs and patience can lead symmetric firms to choose incompatibility
to soften future competition. It also shows that reducing switching costs
through data portability can make compatibility more likely. Consumer effects
are conditional: under a fixed compatibility regime, portability benefits
consumers in their model only when a nonnegative-pricing constraint binds
[@jeon2023compatibility].

Viard supplies an empirical analogy rather than an AI-market estimate. In the
U.S. toll-free-service setting, AT&T and MCI reduced prices following
800-number portability, consistent with lower switching costs increasing price
competition in that setting. Larger contracts experienced larger price drops,
consistent with stronger prior lock-in for larger users
[@viard2007switching]. These results motivate examining portability and
competition, but their estimated magnitudes cannot be transferred to AI
assistants.

Kim analyzes regulation requiring data portability and interoperability in a
two-period Hotelling duopoly with switching costs and network benefits. Without
data-breach accidents, the modeled regulation improves welfare by reducing
switching costs and enlarging network benefits. With breach risk, however,
portability and interoperability raise accident probability; the paper studies
how liability and care incentives can address that risk
[@kim2026portability]. This is a useful limitation for the project: portability
may have security and governance costs that the current normalized payoff model
does not include.

The OECD report provides policy background. It describes how portability can
reduce the cost of recreating data after switching and how interoperability can
facilitate multihoming and preserve network benefits. It also emphasizes legal,
technical, data-protection, and implementation challenges
[@oecd2021portability]. It is not a substitute for peer-reviewed theoretical or
empirical evidence.

Together, these sources justify the chain from switching costs to lock-in and
from portability to changed switching friction or compatibility incentives.
They do not establish that an AI platform will voluntarily make user memory
portable, nor do they identify the project's implementation-cost distribution.

## 3. Behavioral Persistence Beyond Technical Switching Costs

Samuelson and Zeckhauser document status quo bias in experiments and in
consequential choices such as health-plan and retirement-program selections
[@samuelson1988statusquo]. This motivates a hypothesis that a user may remain
with an incumbent even after technical switching friction falls. It does not
show that AI-assistant users behave this way.

The behavioral artifact is implemented and technically verified, but no
participant plays have been analyzed. The safe statement remains:
“Status-quo bias motivates testing whether observed Stay/Switch decisions
depart from a simplified switching-cost benchmark.” It is not permissible to
state that participants or AI-assistant users exhibit status quo bias until
relevant evidence is collected.

## 4. Auction and Mechanism-Design Foundations

Vickrey provides the classic sealed-bid, second-price foundation used for the
standard truthful-bidding benchmark under private values
[@vickrey1961counterspeculation]. Myerson frames the broader problem of
designing an auction for a single object when a seller has incomplete
information about buyers' willingness to pay [@myerson1981optimal]. These
citations support standard allocation and payment reasoning; they do not make
the project's auction application a Vickrey or Myerson result.

The implemented first-price bid function with a reserve is a derivation under
the project's two-bidder, iid `Uniform(0,1)`, risk-neutral benchmark assumptions.
It is not attributed to Vickrey or Myerson. No additional literature source is
needed to claim that project-specific calculation; its assumptions and
validation belong with the computational artifact.

## 5. Closest Prior Work

Compatibility is the closest strategic analogue in Jeon et al.; it is not
silently relabeled as AI memory portability.

| Dimension | Jeon, Menicucci, and Nasr (2023) | Our PS2 |
|---|---|---|
| Market setting | Two firms sell two complementary experience goods/systems | Stylized competing AI assistants |
| Strategic choice | Firms simultaneously choose compatibility or incompatibility; compatibility requires both firms | Each platform chooses Portable or Locked |
| Information structure | Common model primitives; consumers learn product valuations through use; no private firm implementation-cost types | Each platform privately observes a low or high implementation cost |
| Timing | Dynamic baseline with two periods; compatibility is chosen at the start and then fixed while price and purchase competition unfolds | Static simultaneous portability choice |
| Solution concept | Subgame-perfect Nash equilibrium in the dynamic game | Bayesian Nash equilibrium |
| Switching costs | A consumer who changes suppliers in period two incurs a switching cost; history-based pricing matters | Portability incentives motivate the reduced-form payoffs; the auction application uses high/low switching hurdles |
| Data portability | A policy/comparative-static reduction in switching costs | Central platform action and mechanism-design target |
| User competition | Price competition for consumers purchasing systems | Separate stylized auction for one user's next-period primary-assistant slot |
| Behavioral component | No status-quo-bias experiment in the studied model | Exploratory Stay/Switch artifact implemented; no participant evidence analyzed |

Jeon et al. is closest because it endogenizes firms' compatibility choices and
links data portability, switching costs, future competition, and consumer
outcomes in one formal model. The present project changes the information
structure and timing: implementation cost is privately known, the platform
action is static, and the analysis highlights pure and mixed BNE multiplicity.
It then connects that benchmark to a normalized collective objective, an
incentive parameter, and a stylized auction application.

## 6. Project Difference and Research Gap

### Conservative version

Prior work shows that switching costs can create lock-in and that data
portability can alter switching friction and firms' compatibility incentives.
Relative to the closest benchmark, this project studies a stylized AI-assistant
setting in which platforms privately know portability implementation costs and
choose Portable or Locked in a static Bayesian game, then links the resulting
equilibrium multiplicity to social-choice, incentive, and user-allocation
applications.

### Expanded version

The reviewed literature establishes rich links among switching costs, lock-in,
compatibility, data portability, price competition, network benefits, and
security risk. Within this reviewed set, we did not identify a model that
combines a voluntary AI-memory-portability action with privately known platform
implementation costs in a static Bayesian game and then carries its multiple
equilibria through a collective-objective comparison, a verified-portability
incentive, and a user-allocation auction. The project therefore studies a
complementary information structure and application rather than claiming to be
the first analysis of data portability. Its implemented behavioral artifact is
an exploratory demonstration motivated by status quo bias, not a completed
empirical contribution.

### Contribution statement

Prior work studies switching costs, data portability, compatibility, and
platform competition. This project applies those ideas to a stylized
AI-assistant setting with privately known implementation costs, static Bayesian
competition and equilibrium multiplicity, then connects the game to a
collective objective, a portability incentive, a user-allocation auction, and
an implemented exploratory behavioral switching artifact.

## 7. Evidence Boundaries

The reviewed sources do **not** establish that:

- AI memory portability would reproduce the quantitative effects found for
  toll-free-number portability or other digital platforms;
- `r_locked=0.5` and `r_portable=0.2` are empirical switching-hurdle estimates;
- actual AI firms have `c_L=0.2` or `c_H=1.2`, or use the project's payoff
  matrix;
- actual AI firms play one of the computed BNE or select a particular
  equilibrium;
- data portability always raises consumer surplus or welfare;
- lowering technical switching costs removes behavioral inertia, privacy risk,
  security risk, or implementation cost; or
- any participant evidence exists for the behavioral artifact.

Digital-platform portability, 800-number portability, and general switching
cost evidence may be used as motivation and analogy only. The project remains
a normalized, stylized model rather than a calibrated empirical description of
the AI-assistant market.

## Paper-ready concise version

Research on switching costs shows how incompatibility can lock customers in,
reshape entry and pricing incentives, and strengthen incumbency advantages,
although ex ante competition can sometimes offset those effects
[@farrell2007coordination]. Portability offers one way to reduce switching
friction: 800-number portability was followed by lower toll-free-service prices
in Viard's setting [@viard2007switching], while digital-platform models and
policy work emphasize both procompetitive benefits and implementation or
security trade-offs [@kim2026portability; @oecd2021portability]. Our closest
theoretical benchmark is Jeon, Menicucci, and Nasr, who analyze endogenous
compatibility in a dynamic market with switching costs and show that data
portability can make compatibility more likely [@jeon2023compatibility]. Our
project studies a complementary setting: competing AI assistants privately
observe portability implementation costs and make a static Portable/Locked
choice, producing Bayesian equilibrium multiplicity that we connect to a
collective-objective comparison, a portability incentive, and a stylized
user-allocation auction. We treat compatibility as an analogue to memory
portability, not as the same technical object, and make no claim that the
reviewed empirical magnitudes transfer to AI assistants.

## Recommended literature set

### Essential 6

1. `jeon2023compatibility` — closest endogenous compatibility/portability
   benchmark.
2. `farrell2007coordination` — broad switching-cost, lock-in, network-effect,
   and compatibility foundation.
3. `viard2007switching` — strongest empirical portability analogy in the set.
4. `kim2026portability` — digital-platform benefits, network effects, and
   breach-risk limitation.
5. `samuelson1988statusquo` — behavioral hypothesis foundation.
6. `vickrey1961counterspeculation` — concise second-price auction foundation.

### Supporting 3

- `myerson1981optimal` — broad private-information and optimal-auction context;
  the project does not implement the Myerson auction.
- `oecd2021portability` — policy and implementation context, not a substitute
  for peer-reviewed evidence.
- `klemperer1995switching` — concise classic overview of harvesting locked-in
  customers versus investing in market share; useful in an appendix but
  partly redundant with Farrell and Klemperer.
