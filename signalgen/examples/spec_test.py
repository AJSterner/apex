from specanalyzer import EnetRandSFSP

DEFAULT_ADDR = "131.243.171.57"
spec = EnetRandSFSP(DEFAULT_ADDR, 18)
spec.reset()
spec.set_window(185.7, .03, -30)
spec.auto_ref_lvl()
spec.continuous_sweep(False)
spec.take_sweep()


