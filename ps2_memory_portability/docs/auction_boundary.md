# Auction/application boundary

The Phase 3 auction is a stylized allocation analogy with a deliberately narrow
interpretation.

1. The user is not literally sold.
2. The scarce object—one user's primary AI-assistant slot for the next service
   period—is an allocation abstraction.
3. Platform private values are normalized theoretical quantities drawn from an
   independent Uniform(0,1) benchmark. They are not estimated profits.
4. The reserve `r` represents the user's normalized switching or transition
   hurdle.
5. Portability is represented as lowering that hurdle from the locked benchmark
   `r=0.5` to the portable benchmark `r=0.2`. These values are assumptions, not
   measured switching costs.
6. The reserve is placed on the user side of the allocation rule. Alternative
   incidence assumptions—such as a cost borne directly by the platform—could
   produce a different model.
7. The one-shot benchmark abstracts from multi-homing, repeated interaction,
   platform quality dynamics, privacy heterogeneity, network effects,
   endogenous user valuation, platform entry, and multi-user markets.
8. First-price and second-price bidding results rely on symmetric,
   risk-neutral, independent-private-value assumptions and common knowledge of
   the value distribution and reserve.

Within this boundary, the computation supports a limited claim: lowering the
switching hurdle increases the probability that competition produces a
feasible reallocation of the primary-assistant slot. It does not establish how
actual users switch, what real platforms value, or whether an auction should be
used in practice.
