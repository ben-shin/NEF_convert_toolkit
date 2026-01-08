import argparse

def convert_nef_to_tab(input_path, sfh, sfn, output_path, swap, dimx, dimy):
    # Setup constants based on your fid.com and nhsqc.com
    # Dimension X (after swap) = N15
    car_n = 117.006
    sw_n_hz = 2129.472
    sw_n_ppm = sw_n_hz / sfn  # ~35.006 ppm
    
    # Dimension Y (after swap) = H1
    ext_h_start = 11.0
    ext_h_end = 6.0
    ext_h_width = ext_h_start - ext_h_end  # 5.0 ppm
    
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
                height = float(parts[4]) if parts[4] != '.' else 0.0
                vol = float(parts[2]) if parts[2] != '.' else 0.0
                n_ppm = float(parts[6])
                h_ppm = float(parts[8])
                
                res_num = parts[11] if len(parts) > 11 and parts[11] != '.' else ""
                res_name = parts[12] if len(parts) > 12 and parts[12] != '.' else ""
                atom = parts[13] if len(parts) > 13 and parts[13] != '.' else ""
                assig = f"{res_num}{res_name}-{atom}" if res_num else "None"

                # 1. AXIS X (Nitrogen)
                # Position = ( (Carrier + SW/2) - Target_PPM ) / SW * Total_Points
                n_edge = car_n + (sw_n_ppm / 2.0)
                x_axis = ((n_edge - n_ppm) / sw_n_ppm) * dimx
                
                # 2. AXIS Y (Proton - EXTRACTED 11 to 6)
                # In EXT, Point 1 is ext_h_start. 
                y_axis = ((ext_h_start - h_ppm) / ext_h_width) * dimy

                row = [
                    idx, x_axis, y_axis, 0.0, 0.0,
                    n_ppm, h_ppm, n_ppm * sfn, h_ppm * sfh,
                    0.020, 0.100, 0.020 * sfn, 0.100 * sfh,
                    int(x_axis), int(x_axis), int(y_axis), int(y_axis),
                    height, 0.0, vol, 0.0, 1, assig, idx, 1
                ]
                peak_data.append(row)
            except:
                continue

    with open(output_path, 'w') as f:
        f.write("VARS   INDEX X_AXIS Y_AXIS DX DY X_PPM Y_PPM X_HZ Y_HZ XW YW XW_HZ YW_HZ X1 X3 Y1 Y3 HEIGHT DHEIGHT VOL PCHI2 TYPE ASS CLUSTID MEMCNT\n")
        f.write("FORMAT %5d %9.3f %9.3f %6.3f %6.3f %8.3f %8.3f %9.3f %9.3f %7.3f %7.3f %8.3f %8.3f %4d %4d %4d %4d %+e %+e %+e %.5f %d %s %4d %4d\n\n")
        f.write("NULLVALUE -666\n")
        f.write("NULLSTRING *\n\n")
        for p in peak_data:
            f.write("%5d %9.3f %9.3f %6.3f %6.3f %8.3f %8.3f %9.3f %9.3f %7.3f %7.3f %8.3f %8.3f %4d %4d %4d %4d %+14.6e %+14.6e %+14.6e %.5f %d %s %4d %4d\n" % tuple(p))
    print(f"Success: {len(peak_data)} peaks written.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True)
    parser.add_argument('--sfh', type=float, required=True)
    parser.add_argument('--sfn', type=float, required=True)
    parser.add_argument('--dimx', type=int, default=1024)
    parser.add_argument('--dimy', type=int, default=512)
    parser.add_argument('--out', default='peaks.tab')
    args = parser.parse_args()
    convert_nef_to_tab(args.data, args.sfh, args.sfn, args.out, True, args.dimx, args.dimy)
