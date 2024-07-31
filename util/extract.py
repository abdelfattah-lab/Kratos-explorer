import re, os

def extract_info_quartus(path='.'):
    # read information
    fit_successfull = False
    alm_usage = -1
    fmax = -1.0
    rfmax = -1.0

    # if summary file exists
    # read file 'v1.fit.summary'
    fit_path = os.path.join(path, 'v1.fit.summary')
    if os.path.exists(fit_path):
        smy = open(fit_path, 'r')
        fit_summary = smy.read()
        smy.close()
        status_match = re.search(r"Fitter Status : (\w+)", fit_summary)
        if status_match:
            fitter_status: str = status_match.group(1)
            if 'success' in fitter_status.lower():
                fit_successfull = True
                alm_match = re.search(r"Logic utilization \(in ALMs\) : ([\d,]+) \/ ([\d,]+)", fit_summary)
                if alm_match:
                    alm_usage = int(alm_match.group(1).replace(',', ''))
                else:
                    alm_usage = -1

    # if time analysis file exists
    # read file 'v1.sta.rpt'
    sta_rpt_path = os.path.join(path, 'v1.sta.rpt')
    if os.path.exists(sta_rpt_path):
        sta_rpt_file = open(sta_rpt_path, 'r')
        while True:
            line = sta_rpt_file.readline()
            if not line:
                break
            if '; Fmax Summary' in line:
                sta_rpt_file.readline()
                sta_rpt_file.readline()
                sta_rpt_file.readline()
                freqs = sta_rpt_file.readline().strip().split()
                fmax = float(freqs[1])  # fmax in MHz
                rfmax = float(freqs[4])  # restricted fmax in MHz
                break
        sta_rpt_file.close()

    return {'status': fit_successfull, 'alm': alm_usage, 'fmax': fmax, 'rfmax': rfmax}


def extract_info_vtr(path='.', extract_blocks_list=['clb', 'fle']) -> dict:
    # this will extract by default:
    # status for flow (status)
    # fmax (fmax)
    # cirtical path delay (cpd)
    # route channel width (rcw)
    # all elements in extract_blocks_list, e.g. clb, fle,

    # by 2023.10.12: extract:[status, fmax, cpd, rcw, clb, fle, foutm, fouta, gridn, gridtotal, twl, blocks]

    # if extract list is not a list, then we convert it to a list
    if not isinstance(extract_blocks_list, list):
        extract_blocks_list = [extract_blocks_list]

    result_dict = {}
    result_dict['status'] = False
    result_dict['fmax'] = -1.0      # max frequency, MHz
    result_dict['cpd'] = -1.0       # critical path delay, ns
    result_dict['rcw'] = 999999     # route channel width
    result_dict['area_le'] = -1.0   # used area of logic only, in MWTAs
    result_dict['area_r'] = -1.0    # used area of routing, in MWTAs 
    result_dict['foutm'] = 0        # max fanout
    result_dict['fouta'] = 0        # average fanout
    result_dict['gridx'] = 0        # number of grid on x
    result_dict['gridy'] = 0        # number of grid on y
    result_dict['gridtotal'] = 0    # total number of grid
    result_dict['twl'] = 0          # total wire length
    result_dict['wlpg'] = 0         # wire length per grid
    result_dict['blocks'] = 0       # total number of blocks, aka primitive cells
    result_dict['tle'] = 0          # Total number of Logic Elements used
    result_dict['lelr'] = 0         # LEs used for logic and registers
    result_dict['lelo'] = 0         # LEs used for logic only
    result_dict['lero'] = 0         # LEs used for registers only

    # fill default values with -1
    for c in extract_blocks_list:
        result_dict[c] = -1.0

    # vpr output is not same as quartus, the status is at the end of the file, so we need to extract the block usage first and later extratc flow status
    vpr_out_path = os.path.join(path, 'vpr.out')
    # if not exit, then return
    if not os.path.exists(vpr_out_path):
        return result_dict

    f = open(vpr_out_path, 'r')
    for line in f:
        line = line.strip()
        # extract block usage
        if line.startswith('Pb types usage'):
            # this indicates the start of synthesis resourse usage
            # we read maximum 50 lines or if a line is empty, then we stop
            for i in range(50):
                line = f.readline().strip()
                if line == '':
                    # reach the end of the block usage table
                    break
                key, val = [x.strip() for x in line.split(':')[:2]]
                if key in extract_blocks_list:
                    int_val = val
                    try:
                        int_val = int(val)
                    finally:
                        result_dict[key] = int_val
            
        # extract flow status
        if line.startswith('VPR succeeded'):
            result_dict['status'] = True

        # extract critical path delay and fmax
        if line.startswith('Final critical path delay'):
            l_colon = line.find(':')
            info_left = line[l_colon+1:].strip()
            parts = info_left.split()
            result_dict['cpd'] = float(parts[0])
            #Fmax will not be shown if CPD is NaN for any reason
            if len(parts) >= 4:
                result_dict['fmax'] = float(parts[3])

        # extract route channel width
        if line.startswith('Circuit successfully routed with a channel width factor of'):
            if line.endswith('.'):
                line = line[:-1]
            parts = line.split()
            result_dict['rcw'] = int(parts[-1])

        # extract areas
        if line.lstrip().startswith('Total used logic block area'):
            # Logic area
            result_dict['area_le'] = float(line.split(':')[-1].strip())
        if line.lstrip().startswith('Total routing area'):
            # Routing area
            result_dict['area_r'] = float(line.split(':')[-1].strip())
        
        # extract fanout
        if line.startswith('Max Fanout'):
            parts = line.split()
            result_dict['foutm'] = int(float(parts[-1]))
        if line.startswith('Avg Fanout'):
            parts = line.split()
            result_dict['fouta'] = float(parts[-1])

        # extract grid number
        if line.startswith('FPGA sized to') and 'grid' in line:
            line = line.replace(':', '')
            parts = line.split()
            result_dict['gridx'] = int(parts[3])
            result_dict['gridy'] = int(parts[5])
            result_dict['gridtotal'] = int(parts[6])

        # total wire length
        if line.startswith('Total wirelength'):
            line = line.replace(':', '').replace(',', '')
            parts = line.split()
            result_dict['twl'] = int(parts[2])
        # blocks:
        if line.startswith('Circuit Statistics:'):
            line = f.readline().strip()
            line = line.replace(':', '')
            parts = line.split()
            result_dict['blocks'] = int(parts[1])

        # Logic Element (fle) detailed count:
        # Total number of Logic Elements used
        if line.startswith('Total number of Logic Elements used'):
            line = line.replace(':', '').replace(',', '')
            parts = line.split()
            result_dict['tle'] = int(parts[-1])

        # LEs used for logic and registers
        if line.startswith('LEs used for logic and registers'):
            line = line.replace(':', '').replace(',', '')
            parts = line.split()
            result_dict['lelr'] = int(parts[-1])

        # LEs used for logic only
        if line.startswith('LEs used for logic only'):
            line = line.replace(':', '').replace(',', '')
            parts = line.split()
            result_dict['lelo'] = int(parts[-1])

        # LEs used for registers only
        if line.startswith('LEs used for registers only'):
            line = line.replace(':', '').replace(',', '')
            parts = line.split()
            result_dict['lero'] = int(parts[-1])

    f.close()

    # calculate wire length per grid
    if (result_dict['gridtotal'] != 0) and (result_dict['twl'] != 0):
        result_dict['wlpg'] = result_dict['twl'] / result_dict['gridtotal']

    return result_dict