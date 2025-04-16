TITLE na3
: Na current 
: modified from Jeff Magee. M.Migliore may97
: added sh to account for higher threshold M.Migliore, Apr.2002

NEURON {
	SUFFIX na12
	USEION na READ ena WRITE ina
	RANGE  gbar, ar2, thegna, ina_ina
	:GLOBAL vhalfs,sh,tha,qa,Ra,Rb,thi1,thi2,qd,qg,mmin,hmin,q10,Rg,qq,Rd,tq,thinf,qinf,vhalfs,a0s,zetas,gms,smax,vvh,vvs
	RANGE vhalfs,sh,tha,qa,Ra,Rb,thi1,thi2,qd,qg,mmin,hmin,q10,Rg,qq,Rd,tq,thinf,qinf,vhalfs,a0s,zetas,gms,smax,vvh,vvs
}

PARAMETER {
	sh   = 8.886047186457889	(mV)
	gbar = 0.01    				(mho/cm2)	
								
	tha  =  -24.155451306086988	(mV)		: v 1/2 for act	
	qa   = 5.41					(mV)		: act slope (4.5)		
	Ra   = 0.3380714915775742 	(/ms)		: open (v)		
	Rb   = 0.09013136340161398 	(/ms)		: close (v)		

	thi1  = -60.488477521934875	(mV)		: v 1/2 for inact 	
	thi2  = -77.41692349310195 	(mV)		: v 1/2 for inact 	
	qd   = 0.8058343822410788	(mV)	        : inact tau slope
	qg   = 0.6693522946835427    (mV)
	mmin = 0.013671131800210966	
	hmin = 0.008420778920829085			
	q10 = 2.289601426305275
	Rg   = 0.01854277725353276 	(/ms)		: inact recov (v) 	
	Rd   = 0.025712394696815438 (/ms)		: inact (v)	
	qq   = 10        			(mV)
	tq   = -55      			(mV)

	thinf  = -40.114984963535186  	(mV)		: inact inf slope	
	qinf  = 5.760329120353593		(mV)		: inact inf slope 

        vhalfs = -33.73363659219147	(mV)		: slow inact.
        a0s = 0.00036615946706607756	(ms)		: a0s=b0s
        zetas = 13.419130866269455		(1)
        gms = 0.14082624570054866		(1)
        smax = 5.941545585888373		(ms)
        vvh = -53.184249317587984		(mV) 
        vvs = 0.7672523706054653		(mV)
        ar2=1							(1)		: 1=no inact., 0=max inact.
	ena		(mV)	
	Ena = 55	(mV)            : must be explicitly def. in hoc
	celsius
	v 		(mV)
}


UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(pS) = (picosiemens)
	(um) = (micron)
} 

ASSIGNED {
	ina 		(mA/cm2)
    ina_ina  (milliamp/cm2)  :to monitor
	thegna		(mho/cm2)
	minf 		
	hinf 		
	mtau (ms)	
	htau (ms) 	
	sinf (ms)	
	taus (ms)
}
 

STATE { m h s}

BREAKPOINT {
        SOLVE states METHOD cnexp
        thegna = gbar*m*m*m*h*s
	ina = thegna * (v - Ena)
    ina_ina = thegna*(v - Ena)     : define  gbar as pS/um2 instead of mllimho/cm2     :to monitor

} 

INITIAL {
	trates(v,ar2,sh)
	m=minf  
	h=hinf
	s=sinf
}


FUNCTION alpv(v) {
         alpv = 1/(1+exp((v-vvh-sh)/vvs))
}
        
FUNCTION alps(v) {  
  alps = exp(1.e-3*zetas*(v-vhalfs-sh)*9.648e4/(8.315*(273.16+celsius)))
}

FUNCTION bets(v) {
  bets = exp(1.e-3*zetas*gms*(v-vhalfs-sh)*9.648e4/(8.315*(273.16+celsius)))
}

LOCAL mexp, hexp, sexp

DERIVATIVE states {   
        trates(v,ar2,sh)      
        m' = (minf-m)/mtau
        h' = (hinf-h)/htau
        s' = (sinf - s)/taus
}

PROCEDURE trates(vm,a2,sh2) {  
        LOCAL  a, b, c, qt
        qt=q10^((celsius-24)/10)
	a = trap0(vm,tha+sh2,Ra,qa)
	b = trap0(-vm,-tha-sh2,Rb,qa)
	mtau = 1/(a+b)/qt
        if (mtau<mmin) {
		mtau=mmin
		}
	minf = a/(a+b)

	a = trap0(vm,thi1,Rd,qd) : +sh2 raus
	b = trap0(-vm,-thi2,Rg,qg) : - sh2 raus
	htau =  1/(a+b)/qt
        if (htau<hmin) {
		htau=hmin
		}
	hinf = 1/(1+exp((vm-thinf)/qinf)): -sh2 raus
	c=alpv(vm)
        sinf = c+a2*(1-c)
        taus = bets(vm)/(a0s*(1+alps(vm)))
        if (taus<smax) {
		taus=smax
		}
}

FUNCTION trap0(v,th,a,q) {
	if (fabs(v-th) > 1e-6) {
	        trap0 = a * (v - th) / (1 - exp(-(v - th)/q))
	} else {
	        trap0 = a * q
 	}
}	