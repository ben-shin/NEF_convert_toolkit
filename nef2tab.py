import argparse
import subprocess
import os

def get_pipe_dims(ft2_path):
    """Extracts the actual X and Y size from the NMRPipe file header."""
    try:
        cmd = f"nmrPipe -fn HEAD {ft2_path} | grep SIZE"
        result = subprocess.check_output(cmd, shell=True).decode()
        # Example output: Z_SIZE : 1  Y_SIZE : 512  X_SIZE : 1024
        parts = result.split()
        y_size = int(parts[5])
        x_size = int(parts[8])
        return x_size, y_size
    except:
        print("Warning: Could not read .ft2 header. Using default dims.")
        return 1024, 512

def convert_nef_to_tab(input_path, sfh, sfn, ft2_path, output_path, swap):
    dx, dy = get_pipe_dims(ft2_path)
    
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
                
                res_num = parts[11] if len(parts) > 11 and parts[11] != '.' else ""
                res_name = parts[12] if len(parts) > 12 and parts[12] != '.' else ""
                atom = parts[13] if len(parts) > 13 and parts[13] != '.' else ""
                assig = f"{res_num}{res_name}-{atom}" if res_num else "None"

                x_ppm, y_ppm = (n_ppm, h_ppm) if swap else (h_ppm, n_ppm)
                x_sf, y_sf = (sfn, sfh) if swap else (sfh, sfn)

                row = [
                    idx, 0.0, 0.0, 0.0, 0.0,
                    x_ppm, y_ppm, x_ppm * x_sf, y_ppm * y_sf,
                    0.020, 0.100, 0.020 * x_sf, 0.100 * y_sf,
                    0, 0, 0, 0,
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

    print(f"Syncing peaks to {ft2_path} coordinates...")
    sync_cmd = f"pkShift -in {output_path} -out {output_path} -unfold -real -ppm -spec {ft2_path}"
    os.system(sync_cmd)
    print(f"Success. Peaks in {output_path} are now synced to the spectrum grid.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True)
    parser.add_argument('--ft2', required=True, help='Path to hsqc.ft2')
    parser.add_argument('--sfh', type=float, required=True)
    parser.add_argument('--sfn', type=float, required=True)
    parser.add_argument('--out', default='peaks.tab')
    parser.add_argument('--swap', action='store_true')
    args = parser.parse_args()
    convert_nef_to_tab(args.data, args.sfh, args.sfn, args.ft2, args.out, args.swap)
