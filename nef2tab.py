import argparse

def convert_nef_to_tab(input_path, sfh, sfn, output_path):
    # --- EXACT BOUNDS FROM YOUR REMARK ROI ---
    # Proton (1H)
    h_p1 = 12.709
    h_pn = 4.684
    h_n  = 514
    
    # Nitrogen (15N)
    n_p1 = 134.509
    n_pn = 99.400
    n_n  = 342
    
    try:
        with open(input_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File {input_path} not found.")
        return

    peak_data = []
    is_peak_loop = False
    
    for line in lines:
        clean_line = line.strip()
        if '_nef_peak.index' in clean_line:
            is_peak_loop = True
            continue
        if is_peak_loop:
            if clean_line == 'stop_' or clean_line.startswith('save_'):
                is_peak_loop = False
                continue
            if clean_line.startswith('_') or not clean_line:
                continue

            parts = clean_line.split()
            try:
                idx = int(parts[0])
                vol = float(parts[2]) if parts[2] != '.' else 0.0
                height = float(parts[4]) if parts[4] != '.' else 0.0
                n_ppm = float(parts[6])
                h_ppm = float(parts[8])
                
                # Assignment
                res_num = parts[11] if len(parts) > 11 and parts[11] != '.' else ""
                res_name = parts[12] if len(parts) > 12 and parts[12] != '.' else ""
                atom = parts[13] if len(parts) > 13 and parts[13] != '.' else ""
                assig = f"{res_num}{res_name}-{atom}" if res_num else "None"

                # --- LINEAR INTERPOLATION MATH ---
                # Formula: Point = 1 + (PPM_val - PPM_start) / (PPM_end - PPM_start) * (Total_Points - 1)
                
                # If Nitrogen is X-axis in nmrDraw:
                x_axis = 1 + (n_ppm - n_p1) / (n_pn - n_p1) * (n_n - 1)
                
                # If Proton is Y-axis in nmrDraw:
                y_axis = 1 + (h_ppm - h_p1) / (h_pn - h_p1) * (h_n - 1)

                row = [
                    idx, x_axis, y_axis, 0.0, 0.0,
                    n_ppm, h_ppm, n_ppm * sfn, h_ppm * sfh,
                    0.020, 0.100, 1.0, 1.0,
                    int(x_axis), int(x_axis), int(y_axis), int(y_axis),
                    height, 0.0, vol, 0.0, 1, assig, idx, 1
                ]
                peak_data.append(row)
            except:
                continue

    # Writing the table with correct NMRPipe padding
    with open(output_path, 'w') as f:
        f.write("VARS   INDEX X_AXIS Y_AXIS DX DY X_PPM Y_PPM X_HZ Y_HZ XW YW XW_HZ YW_HZ X1 X3 Y1 Y3 HEIGHT DHEIGHT VOL PCHI2 TYPE ASS CLUSTID MEMCNT\n")
        f.write("FORMAT %5d %9.3f %9.3f %6.3f %6.3f %8.3f %8.3f %9.3f %9.3f %7.3f %7.3f %8.3f %8.3f %4d %4d %4d %4d %+e %+e %+e %.5f %d %s %4d %4d\n\n")
        f.write("NULLVALUE -666\n")
        f.write("NULLSTRING *\n\n")
        for p in peak_data:
            f.write("%5d %9.3f %9.3f %6.3f %6.3f %8.3f %8.3f %9.3f %9.3f %7.3f %7.3f %8.3f %8.3f %4d %4d %4d %4d %+14.6e %+14.6e %+14.6e %.5f %d %s %4d %4d\n" % tuple(p))
    print(f"Success: {len(peak_data)} peaks mapped to ROI bounds.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True)
    parser.add_argument('--sfh', type=float, required=True)
    parser.add_argument('--sfn', type=float, required=True)
    parser.add_argument('--out', default='peaks.tab')
    args = parser.parse_args()
    convert_nef_to_tab(args.data, args.sfh, args.sfn, args.out)
