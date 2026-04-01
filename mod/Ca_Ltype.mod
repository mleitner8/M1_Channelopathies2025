: L-type (Cav1-like) high-voltage activated calcium channel (phenomenological)
: Intended for distal apical tuft plateau support (slow inactivation).
:
: Notes:
: - Uses HH-style activation/inactivation with slow, incomplete inactivation.
: - Includes hTauFac so you can tune inactivation speed from Python.

NEURON {
    SUFFIX Ca_Ltype
    USEION ca READ eca WRITE ica
    RANGE gCa_Ltypebar, gCa_Ltype, ica
    RANGE hTauFac
}

UNITS {
    (S) = (siemens)
    (mV) = (millivolt)
    (mA) = (milliamp)
}

PARAMETER {
    gCa_Ltypebar = 0.000001 (S/cm2)
    hTauFac = 1
}

ASSIGNED {
    v (mV)
    eca (mV)
    ica (mA/cm2)
    gCa_Ltype (S/cm2)

    mInf
    mTau (ms)
    hInf
    hTau (ms)
}

STATE {
    m
    h
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    gCa_Ltype = gCa_Ltypebar*m*m*h
    ica = gCa_Ltype*(v-eca)
}

DERIVATIVE states {
    rates()
    m' = (mInf-m)/mTau
    h' = (hInf-h)/hTau
}

INITIAL {
    rates()
    m = mInf
    h = hInf
}

PROCEDURE rates() {
    UNITSOFF
    : Activation: high threshold, relatively slow (Cav1-like)
    mInf = 1/(1+exp((v - -20)/-6.5))
    : ms; slower at hyperpolarized, faster when depolarized
    mTau = 1 + 4/(1+exp((v - -25)/5))

    : Inactivation: slow and incomplete
    : Keep hInf relatively high so channel remains available during plateaus.
    hInf = 0.7 + 0.3/(1+exp((v - -40)/7))
    : Very slow inactivation time constant (ms)
    hTau = (150 + 250/(1+exp((v - -35)/5))) * hTauFac
    UNITSON
}
