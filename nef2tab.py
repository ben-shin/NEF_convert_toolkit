import argparse
import sys

def convert_nef_to_tab(input_path, sfh, sfn, output_path="peaks.tab", swap=False):
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
            
            # 0: index, 2: volume, 4: height, 6: pos_1 (N15), 8: pos_2 (H1)
            # 10: chain, 11: seq_code, 12: res_name, 13: atom_name
            try:
                idx = int(parts[0])
                vol = float(parts[2]) if parts[2] != '.' else 0.0
                height = float(parts[4]) if parts[4] != '.' else 0.0
                n_ppm = float(parts[6])
                h_ppm = float(parts[8])
                
                res_num = parts[11] if len(parts) > 11 and parts[11] != '.' else ""
                res_name = parts[12] if len(parts) > 12 and parts[12] != '.' else ""
                atom = parts[13] if len(parts) > 13 and parts[13] != '.' else ""
                
                assig = f"{res_num}{res_name}-{atom}" if res_num else "None"

                if swap:
                    x_ppm, y_ppm = n_ppm, h_ppm
                    x_sf, y_sf = sfn, sfh
                else:
                    x_ppm, y_ppm = h_ppm, n_ppm
                    x_sf, y_sf = sfh, sfn
                
                row = {
                    'INDEX': idx, 'X_AXIS': 0.0, 'Y_AXIS': 0.0,
                    'DX': 0.0, 'DY': 0.0, 'X_PPM': x_ppm, 'Y_PPM': y_ppm,
                    'X_HZ': x_ppm * x_sf, 'Y_HZ': y_ppm * y_sf,
                    'XW': 0.020, 'YW': 0.100, 'XW_HZ': 0.020 * x_sf, 'YW_HZ': 0.100 * y_sf,
                    'X1': 0, 'X3': 0, 'Y1': 0, 'Y3': 0,
                    'HEIGHT': height, 'DHEIGHT': 0.0, 'VOL': vol,
                    'PCHI2': 0.0, 'TYPE': 1, 'ASS': assig,
                    'CLUSTID': idx, 'MEMCNT': 1
                }
                peak_data.append(row)
            except (ValueError, IndexError):
                continue

    if not peak_data:
        print("Warning: No peaks found. Check if the NEF file contains a populated _nef_peak loop.")
        return

    with open(output_path, 'w') as f:
        f.write("VARS   INDEX X_AXIS Y_AXIS DX DY X_PPM Y_PPM X_HZ Y_HZ XW YW XW_HZ YW_HZ X1 X3 Y1 Y3 HEIGHT DHEIGHT VOL PCHI2 TYPE ASS CLUSTID MEMCNT\n")
        f.write("FORMAT %5d %9.3f %9.3f %6.3f %6.3f %8.3f %8.3f %9.3f %9.3f %7.3f %7.3f %8.3f %8.3f %4d %4d %4d %4d %+e %+e %+e %.5f %d %s %4d %4d\n\n")
        f.write("NULLVALUE -666\n")
        f.write("NULLSTRING *\n\n")
        
        for p in peak_data:
            line = (
                f"{p['INDEX']:5d} {p['X_AXIS']:9.3f} {p['Y_AXIS']:9.3f} {p['DX']:6.3f} {p['DY']:6.3f} "
                f"{p['X_PPM']:8.3f} {p['Y_PPM']:8.3f} {p['X_HZ']:9.3f} {p['Y_HZ']:9.3f} "
                f"{p['XW']:7.3f} {p['YW']:7.3f} {p['XW_HZ']:8.3f} {p['YW_HZ']:8.3f} "
                f"{p['X1']:4d} {p['X3']:4d} {p['Y1']:4d} {p['Y3']:4d} "
                f"{p['HEIGHT']:+e} {p['DHEIGHT']:+e} {p['VOL']:+e} "
                f"{p['PCHI2']:.5f} {p['TYPE']:d} {p['ASS']} {p['CLUSTID']:4d} {p['MEMCNT']:4d}\n"
            )
            f.write(line)
    print(f"Success: {len(peak_data)} peaks written to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert NEF peak lists to nmrDraw .tab format')
    parser.add_argument('--data', required=True, help='Path to the input .nef file')
    parser.add_argument('--sfh', type=float, required=True, help='Spectrometer frequency for Hydrogen (MHz)')
    parser.add_argument('--sfn', type=float, required=True, help='Spectrometer frequency for Nitrogen (MHz)')
    parser.add_argument('--out', default='peaks.tab', help='Output filename')
    parser.add_argument('--swap', action='store_true', help='Swap axes (Use if N15 is on X-axis)')
    
    args = parser.parse_args()
    convert_nef_to_tab(args.data, args.sfh, args.sfn, args.out, args.swap)
