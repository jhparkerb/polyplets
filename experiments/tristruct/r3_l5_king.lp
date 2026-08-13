% r3_l5_king.lp — T(n,H) as an ASP program (R3 lane L5).
%
% T(n,H) = number of answer sets: king-connected n-cell subsets of the box
% [0,n) x [0,h), normalized min-x = 0, min-y = 0, max-y = h-1 (height
% exactly h, counted up to translation; width <= n is a theorem for
% connected n-cell sets, so the box loses nothing).
%
% Connectivity is STATED, not implemented: reach/2 is defined by the
% least-fixed-point (stable-model) semantics of the program. The solver's
% unfounded-set machinery — third-party code — is what rejects circular
% justifications; no line of this file implements a connectivity algorithm.
%
% Evaluate (clingo not installed on gympie 2026-08-12; MacPorts has it:
%   sudo port install clingo ):
%
%   clingo r3_l5_king.lp -c n=5 -c h=3 -q 0
%
% and read "Models : 248". All auxiliary atoms (preceded/root/reach) are
% functionally determined by in/2, so the raw model count equals the
% projected count; --project=show with #show in/2 makes that explicit.

#const n=5.
#const h=3.

cellx(0..n-1).
celly(0..h-1).

% choose exactly n cells
{ in(X,Y) : cellx(X), celly(Y) } = n.

% normalization: touch column 0, row 0, row h-1
touchleft :- in(0,Y).
touchbot  :- in(X,0).
touchtop  :- in(X,h-1).
:- not touchleft.
:- not touchbot.
:- not touchtop.

% king adjacency between occupied cells
adj(X1,Y1,X2,Y2) :- in(X1,Y1), in(X2,Y2), |X1-X2| <= 1, |Y1-Y2| <= 1,
                    (X1,Y1) != (X2,Y2).

% root = first occupied cell in column-major order
preceded(X,Y) :- in(X,Y), in(X2,Y2), X2*h+Y2 < X*h+Y.
root(X,Y) :- in(X,Y), not preceded(X,Y).

% reach = least fixed point from the root
reach(X,Y)   :- root(X,Y).
reach(X2,Y2) :- reach(X,Y), adj(X,Y,X2,Y2).

% connectivity as a constraint
:- in(X,Y), not reach(X,Y).

#show in/2.
