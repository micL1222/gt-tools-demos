# Claim–Source Map

Statuses apply to the wording in the **Safe formulation** column. A source can
support a general mechanism or an analogy without supplying evidence for the
AI-assistant market.

| ID | Paper claim | Status | Source(s) | Safe formulation | Qualification / prohibited extension |
|---|---|---|---|---|---|
| A | Switching costs can generate lock-in and alter competition. | **Supported** | `farrell2007coordination`; `klemperer1995switching` | Switching costs can bind customers to vendors, create ex post market power, and change pricing, entry, and market-share incentives. | Do not write that switching costs always weaken competition or always raise prices. |
| B | Portability can reduce switching frictions. | **Supported** | `jeon2023compatibility`; `viard2007switching`; `kim2026portability`; `oecd2021portability` | Portability reduces switching costs by construction in the cited models/policy framework, and 800-number portability removed a concrete switching friction in Viard's setting. | Do not infer an AI-specific magnitude or that all useful memory can be transferred without loss. |
| C | Firms may strategically choose incompatibility or compatibility. | **Supported** | `jeon2023compatibility`; contextual support from `farrell2007coordination` | Firms' compatibility choices can respond strategically to switching costs and future competition; Jeon et al. derive conditions under which symmetric firms choose incompatibility. | Their dynamic complementary-products model is not our static private-cost Bayesian game. |
| D | Reducing switching friction can strengthen competition in at least some real-world portability settings. | **Supported** | `viard2007switching` | In the studied toll-free-service market, AT&T and MCI cut prices in response to 800-number portability, consistent with stronger price competition. | This is a setting-specific price result, not a universal portability effect or an AI estimate. |
| E | Portability/interoperability may also involve privacy or security trade-offs. | **Supported in the cited model** | `kim2026portability`; policy context from `oecd2021portability` | Kim's model shows that required portability/interoperability can raise data-breach accident probability even while producing switching-cost and network benefits. | Do not state that a measured breach increase has been established for AI memory portability. |
| F | Status quo bias may cause persistence beyond a simple switching-cost benchmark. | **Partially supported** | `samuelson1988statusquo` | General status-quo-bias evidence motivates testing whether Stay/Switch choices persist after modeled technical friction falls. | The source does not study AI assistants, and the planned artifact has collected no behavioral evidence. |
| G | Second-price auctions have a standard truthful-bidding benchmark under private values. | **Supported** | `vickrey1961counterspeculation` | Under the standard independent-private-value benchmark, a sealed-bid second-price auction provides the truthful-bidding comparison used by the application. | The project's switching-hurdle reserve and first-price bid function are project-specific, not Vickrey's portability design. |
| H | Auction design concerns allocation/payment rules under private information. | **Supported** | `myerson1981optimal` | Myerson studies optimal single-object auction design when the seller is imperfectly informed about buyers' willingness to pay. | The project does not implement or claim a Myerson-optimal auction. |
| I | Private implementation-cost types can generate the project's two pure BNE and mixed equilibrium. | **Not a literature claim; supported by project artifacts** | Phase 2 model, tests, and output | Under the stated normalized payoff model and benchmark parameters, the direct checker returns the documented BNE. | Do not cite Jeon et al. for our private types or exact multiplicity. |
| J | Portability always improves consumer surplus or welfare. | **Not supported** | Contrary qualifications in `jeon2023compatibility` and `kim2026portability` | Portability's effects depend on pricing constraints, compatibility regime, network benefits, breach risk, and other model assumptions. | Never use the unconditional “always improves welfare” claim. |
| K | The benchmark cost and reserve parameters are empirical estimates for AI markets. | **Not supported** | None | The values are normalized assumptions used for a transparent computational benchmark. | Do not label `c_L`, `c_H`, `r_locked`, or `r_portable` as measured or calibrated facts. |
| L | Actual AI firms follow the project's BNE. | **Needs more evidence** | None | The BNE are predictions of the stated stylized game, not observations of firm conduct. | Do not present equilibrium behavior as an empirical fact. |

## Usage rule

Literature citations should support the general economic or behavioral premise.
Project artifacts should support the project's own equilibrium, welfare,
mechanism, and simulation results. Neither evidence type should be used as a
substitute for the other.
