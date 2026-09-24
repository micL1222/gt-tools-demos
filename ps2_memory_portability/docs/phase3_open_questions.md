# Phase 3 open questions

This file records decisions that remain open. It is not an implementation specification, and no assumption below has been added to the Phase 2 Bayesian game.

## Social choice

- What is the appropriate definition of user welfare under portable versus locked memory?
- What collective objective should be evaluated?
- Are normalized platform utilities and a future user-utility measure directly comparable?
- If the objective uses weights, what evidence or normative argument justifies them?
- Should welfare be reported as separate stakeholder components before any aggregation?

## Mechanism design

- What is the precise intervention: subsidy, certification, compliance rule, interoperability standard, or another instrument?
- Who finances or administers the intervention?
- What reports or actions does the mechanism elicit?
- Does the mechanism target equilibrium existence, adoption incentives, or equilibrium selection?
- What feasibility, incentive, or budget constraints must the mechanism satisfy?

## Auction or allocation application

- What exactly is the scarce resource: one user's primary assistant relationship, access to a user segment, or another stylized allocation?
- What does a platform's private value (v_i) represent?
- Is switching cost borne by the user, incorporated into an acceptance rule, or reflected elsewhere?
- What behavioral and information assumptions justify first-price versus second-price bidding?
- What reserve rule and tie-breaking rule are appropriate?
- How should user surplus be defined without pretending that users are literally sold?
- Where does the auction analogy cease to describe actual AI-assistant competition?

## Behavioral artifact

- Which friction is central: status-quo bias, perceived migration risk, privacy concern, or another mechanism?
- What experimental framing distinguishes rational switching cost from behavioral inertia?
- What variables can be collected without real user data or unsupported inference?
- What evidence boundary should accompany the Hugging Face demonstration?

## Cross-cutting research decisions

- How should equilibrium selection be studied when `LL` and `PL` coexist?
- Should correlated platform costs replace the baseline independence assumption?
- Is binary portability sufficient, or should later work allow partial portability?
- Which normalized parameters should be varied, and what evidence would be needed before empirical calibration?
