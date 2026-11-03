# Outward travel: radial energy output versus wheel energy input

The user correctly questioned the earlier climber numbers. **Climber mass has
not been sized or specified.** The earlier 10 kg per climber was an arbitrary
sensitivity input, not a derived mass or a mission requirement. The primary
comparison now uses a **zero-climber-mass limit**, with 1% and 10% of payload
mass per climber as explicitly labeled sensitivities. A massless climber is not
a physical proposal.

The earlier approximately 4.8 MW headline also failed to distinguish the
channels: it was predominantly **wheel electrical input in a constant-spin
example**, not power used by the outward-moving climbers. Constant spin was an
illustrative control choice, not a requirement supplied by the user.

## What produces and what consumes power

For a moving point mass \(m\) at radius \(r\), radial speed \(\dot r\), radial
acceleration \(\ddot r\), hub speed \(\omega\), and hub acceleration \(\alpha\):

\[
F_r=m(\ddot r-r\omega^2),\qquad
F_t=m(r\alpha+2\dot r\omega).
\]

The force is the force **on the moving mass**. Radial-actuator mechanical power is

\[
P_r=F_r\dot r=m(\ddot r-r\omega^2)\dot r.
\]

On a steady outward traverse, \(\dot r>0\), \(\ddot r=0\), hence
**\(P_r<0\)**: the moving load drives the radial mechanism. The climber needs to
control/brake this motion and can potentially generate power. The existing
no-recovery comparison treats that negative work as dissipated, not consumed.
During inward return, the sign generally reverses and the radial drive supplies
positive work proportional to the unsized returning climber mass.

For constant spin, tangential driving power supplied through the rotating hub is

\[
P_w=F_t\,r\omega=2m\omega^2r\dot r.
\]

For an outward rest-to-rest traverse from \(r_1\) to \(r_2\):

\[
\Delta K_\theta=\tfrac12m\omega^2(r_2^2-r_1^2),\qquad
W_w=2\Delta K_\theta,\qquad W_r=-\Delta K_\theta.
\]

Thus outward radial work is extractable while the wheel drive is supplying
energy. Without recovery, the wheel supplies twice the load's rotational
kinetic-energy gain and the radial mechanism dissipates the other half.
That is a consequence of the **constant-spin branch**, not a universal energy
penalty of all climber operation.

## Allowing rotation speed to vary

Let \(I_0\) be the inertia of components at fixed radius and
\(I(t)=I_0+\sum m r^2\). Then

\[
\tau_w=\frac{d(I\omega)}{dt}=I\alpha+\dot I\omega,\qquad
P_w=I\omega\alpha+\dot I\omega^2.
\]

Including radial kinetic energy gives the work identity

\[
P_w+\sum P_r=
\frac{d}{dt}\left(\tfrac12 I\omega^2+
\tfrac12\sum m\dot r^2\right).
\]

If external driving torque is zero, \(I\omega\) is conserved and the machine
slows as the loads move out. Rotational energy can then become radial motion
or extractable radial work. It is drawn from the machine's existing motion;
the target release velocity still has to be reached.

We cannot calculate this spin history defensibly without the tether/frame
inertia and a chosen control trajectory. Nor should we introduce an arbitrary
flywheel to supply it. The next dynamic model must calculate the actual
machine's inertia, wheel-speed limits, required release state, and power history
together. The variable-spin energy identity is implemented and tested, but no
variable-spin feasible cycle is asserted.

## Can outward braking power be reused immediately?

Potentially: a reversible climber drive could run as a generator, its inverter
could supply a shared electrical bus, and the wheel drives could consume that
power at the same instant. This describes a possible conversion mechanism,
without a battery. It still needs grip/drive compatibility, rated hardware,
conversion efficiencies, power transfer and concurrent demand to be established.

For that candidate, an instantaneous balance would be

\[
P_{\rm solar}+\eta_g\max(-P_r,0)
\ge\frac{\max(P_w,0)}{\eta_w}
+\frac{\max(P_r,0)}{\eta_c}+P_{\rm aux}.
\]

Surplus power would need to be curtailed or dissipated, not stored or credited
to a later phase. With perfect conversion, positive outbound net demand remains
the kinetic-energy increase. The present results still take **no recovery
credit**; the equation above is a candidate to demonstrate and size, not an
adopted efficiency or an assertion that the hardware exists.

## What changes if the tether is spooled instead?

Controlled outward payout can extract energy at the apex spool at approximately
\(T\,\dot L\) for a simple routing, making the extraction/holding hardware
stationary relative to the apex rather than riding as a climber.
The changing moment of inertia and required final payload speed remain.
Spooling does not automatically eliminate wheel work or create net free
orbital-launch energy.

Payout could remove a traveling climber or change its role, but adds moving
cable mass, drum inertia, bend/fatigue limits, retraction work and a new return
sequence. The initial proposal already includes apex spools, so comparing this
branch is reasonable. It has **not** been silently substituted for the user's
extended-sling architecture.

The useful next comparison is constant-spin climbers, controlled variable-spin
climbers, and controlled payout, with the same release state, direct-solar
restriction and full mass accounting. The first two require less architecture
change; their feasibility has not yet been settled.
