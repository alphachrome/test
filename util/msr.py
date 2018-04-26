import subprocess

def msr(cpuno, regno):
    cmd = "rdmsr -p {} {}".format(cpuno, regno)
    result = subprocess.check_output(cmd, shell=True)
    return int('0x'+result,0)

mask = lambda m: sum([2**b for b in range(m)])

REG= {
    "HWP_ENABLE": (0x770,0,1),
    "HWP_LOWEST_PERF": (0x771,31,8), 
    "HWP_EFFICIENT_PERF": (0x771,23,8), 
    "HWP_GUARANTEED_PERF": (0x771,15,8),
    "HWP_HIGHEST_PERF": (0x771,7,8),
    "PKG_HDC_CTL": (0xDB0,0,1),
    "CLK_MOD_EN": (0x19A,4,1),
    "CLK_MOD_DUTY": (0x19A,3,3)
}

class Msr:
    def __init__(self, cpu=0):
        self.cpu=cpu
        
    def get(self, reg_name):     
        reg = REG[reg_name][0]
        pos = REG[reg_name][1]
        num = REG[reg_name][2]
        
        val = msr(self.cpu, reg)
        return (val >> (pos-num+1)) & mask(num)
        
    def gets(self, reg_name):
        return reg_name+": "+str(self.get(reg_name))

cpu0 = Msr(0)

for r in REG.keys():
    print cpu0.gets(r)

IA32_HWP_REQUEST_PKG=0x772  # Conveys OSPM's control hints (Min, Max, Activity Window, Energy
                            # Performance Preference, Desired) for all logical processor in
                            # the physical package.
IA32_HWP_INTERRUPT=0x773    # Controls HWP native interrupt generation (Guaranteed Performance
                            # changes, excursions).
IA32_HWP_REQUEST=0x774      # Conveys OSPM's control hints (Min, Max, Activity Window, Energy
                            # Performance Preference, Desired) for a single logical processor.
IA32_HWP_PECI_REQUEST_INFO=0x775
                            # Conveys embedded system controller requests to override some of
                            # the OS HWP Request settings via the PECI mechanism.
IA32_HWP_STATUS=0x777       # Status bits indicating changes to Guaranteed Performance and
                            # excursions to Minimum Performance.
IA32_THERM_STATUS=0x19C #[bits 15:12]
                            # Conveys reasons for performance excursions.
MSR_PPERF=0x64E             # Productive Performance Count.
