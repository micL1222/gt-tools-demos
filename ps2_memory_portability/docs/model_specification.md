# Formal model specification

## Scope and evidence boundary

This appendix specifies the Phase 2 benchmark for **Stay or Switch? Strategic Memory Portability in Competing AI Assistants**. It is a stylized, static Bayesian game. Its payoff numbers are normalized theoretical parameters, not estimates of actual firms' costs or profits.

## Notation

| Symbol | Meaning |
|---|---|
| (i\in\{A,B\}) | Platform player |
| (c_i\in\{c_L,c_H\}) | Privately observed portability implementation cost |
| (p\in(0,1)) | Common prior probability of a low-cost type |
| (a_i\in\{P,L\}) | Portable or Locked action |
| (s_i=(s_i(c_L),s_i(c_H))) | Pure type-contingent strategy |
| (q\) | Probability the rival chooses Portable |
| (u_i) | Platform (i)'s normalized payoff |

Benchmark values are (c_L=0.2), (c_H=1.2), and (p=0.7).

## Players, types, prior, and actions

There are two generic platforms, A and B. Nature independently draws each platform's type:

\[
\Pr(c_i=c_L)=p,\qquad \Pr(c_i=c_H)=1-p.
\]

Each platform observes only its own type. It then chooses (P) (Portable) or (L) (Locked). The platforms choose simultaneously, so neither observes the rival's current action.

The four joint type probabilities are

\[
p^2,\quad p(1-p),\quad (1-p)p,\quad (1-p)^2
\]

for ((c_L,c_L),(c_L,c_H),(c_H,c_L),(c_H,c_H)), respectively.

## Timing and information

1. Nature independently draws (c_A) and (c_B).
2. A observes (c_A), not (c_B).
3. B observes (c_B), not (c_A).
4. A and B simultaneously choose (P) or (L).
5. Payoffs are realized.

Because the game is static and contains private types, the primary solution concept is Bayesian Nash equilibrium, not SPNE or PBE.

## Strategy space

A pure Bayesian strategy is a complete map from own type to action. The notation is ordered as `(low-type action, high-type action)`:

| Strategy | Low type | High type |
|---|---|---|
| `LL` | Locked | Locked |
| `PL` | Portable | Locked |
| `LP` | Locked | Portable |
| `PP` | Portable | Portable |

These labels are strategies, not realized action profiles.

## Payoffs

For own cost (c_i),

\[
\begin{array}{c|cc}
 & P & L\\ \hline
P & 2-c_i & -1-c_i\\
L & 1 & 0
\end{array}
\]

Rows are own actions and columns are rival actions. Mutual portability can produce coordination or interoperability gains, unilateral portability is disadvantageous, and locking against a portable rival yields 1. These are modeling assumptions.

## Expected utility and best response

If the rival chooses Portable with probability (q),

\[
EU(P\mid c_i)=q(2-c_i)+(1-q)(-1-c_i)=3q-1-c_i,
\]

and

\[
EU(L\mid c_i)=q.
\]

Therefore Portable is a weak best response if and only if

\[
3q-1-c_i\ge q
\iff 2q-1\ge c_i.
\]

For a rival pure strategy, (q(LL)=0), (q(PL)=p), (q(LP)=1-p), and (q(PP)=1).

## Type-level pure BNE definition

A pure profile ((s_A,s_B)) is a Bayesian Nash equilibrium when, for each platform (i) and each positive-probability type (c_i), the prescribed action satisfies

\[
EU_i(s_i(c_i),s_{-i}\mid c_i)
\ge
EU_i(a_i',s_{-i}\mid c_i)
\quad\text{for every }a_i'\in\{P,L\}.
\]

The implementation checks all four type-level constraints directly for every one of the (4\times4=16) pure strategy profiles. It does not rely only on an ex-ante comparison between complete strategies.

## Benchmark pure equilibria

Against `LL`, (q=0). Both types strictly prefer Locked, so `(LL,LL)` is a pure BNE.

Against `PL`, (q=0.7). The low type obtains (0.9) from Portable and (0.7) from Locked; the high type obtains (-0.1) from Portable and (0.7) from Locked. Thus `(PL,PL)` is a pure BNE.

The exhaustive profile check rejects all other pure profiles, including asymmetric profiles. Hence the benchmark has exactly two **pure** BNE:

\[
(LL,LL)\quad\text{and}\quad(PL,PL).
\]

This is not a claim that there are exactly two BNE of all kinds.

## PL threshold and multiplicity

For symmetric `PL`, (q=p). The low type chooses Portable when

\[
p\ge p^*=\frac{1+c_L}{2}.
\]

At (c_L=0.2), (p^*=0.6). Equality is included because BNE permits weak best responses. The high type remains Locked for all feasible (p) under (c_H=1.2). Therefore `(LL,LL)` persists while `(PL,PL)` becomes sustainable at (p=0.6), creating equilibrium multiplicity rather than selecting a unique outcome.

## Symmetric type-specific mixed candidate

Fix high-cost types at Locked and let a low-cost type choose Portable with probability (x). Then (q=px). Low-type indifference requires

\[
q^*=\frac{1+c_L}{2},\qquad
x^*=\frac{1+c_L}{2p}.
\]

At the benchmark, (q^*=0.6) and (x^*=6/7\approx0.8571428571). High types strictly prefer Locked at this (q). This is the symmetric type-specific mixed equilibrium implied by low-type indifference under the baseline structure; it is not presented as an exhaustive mixed-equilibrium theorem for every parameterization. At (p=0.6), (x^*=1), so the expression collapses to pure `PL` and is not a distinct interior mixed equilibrium.

## Endpoint caveat

Formal sweeps use (0<p<1). At (p=0) or (p=1), one type has zero prior probability and its action is not disciplined in the same way by the ordinary ex-ante BNE condition. The software flags those priors as boundary cases instead of silently applying the full-support checker.

## Interpretation boundary

The code establishes equilibrium properties of this benchmark under its stated assumptions. It does not establish empirical implementation costs, actual company behavior, equilibrium selection, user welfare, or the effects of an intervention. Those questions require additional modeling or evidence in later phases.
