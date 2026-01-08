import pandas as pd
import argparse
import sys

def convert_nef_to_nmrdraw(input_path, sfh, sfn, output_path="peaks.tab"):
  try:
    with open(input_path, 'r') as f:
      nef_text = f.read()
  except FileNotFoundError:
    print(f"Error: file not found.")
    return

  lines = nef_text.strip().split('\n')
  peak_data = []
  is_peak_loop = False

  for line in lines:
    if '_nef_peak.index' in line:
      is_peak_loop = True
      continue
    if is_peak_look:
      parts = line.split()
      if not parts or parts[0] == 'stop_':
        is_peak_loop = False
        continue
      if parts[0].startswith('_'): 
        continue

      idx = int(parts[0])
      vol = float(parts[2]) if parts[2] != '.' else 0.0
      height = float(parts[4]) if parts[4] != '.' else 0.0
      n_ppm = float(parts[6])  # N15
      h_ppm = float(parts[8])  # H1

      res_num = parts[11] if parts[11] != '.' else ""
      res_name = parts[12] if parts[12] != '.' else ""
      atom = parts[13] if parts[13] != '.' else ""
      assig = f"{res_num}{res_name}-{atom}" if res_num else "None"
      
      row = {
        'INDEX': idx,
        'X_AXIS': n_ppm * 1.0,
        'Y_AXIS': h_ppm * 1.0,
        'DX': 0.000,
        'DY': 0.000,
        'X_PPM': n_ppm,
        'Y_PPM': h_ppm, # Pipe often swaps these labels
        'X_HZ': n_ppm * sfn,
        'Y_HZ': h_ppm * sfh,
        'XW': 0.100,
        'YW': 0.020, # Linewidths in PPM
        'XW_HZ': 0.100 * sfn,
        'YW_HZ': 0.020 * sfh,
        'X1': 0, 'X3': 0,
        'Y1': 0, 'Y3': 0,
        'HEIGHT': height, 'DHEIGHT': 0.0, 'VOL': vol,
        'PCHI2': 0.00000, 'TYPE': 1, 'ASS': assig,
        'CLUSTID': idx, 'MEMCNT': 1
        }
      peak_data.append(row)

  with open(output_file, 'w') as f:
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

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Convert NEF to nmrDraw peaklist")
  parser.add_argument('--data', required=True, help='Path to the input .nef file')
  parser.add_argument('--sfh', type=float, required=True, help='Spectrometer frequency for Hydrogen (MHz)')
  parser.add_argument('--sfn', type=float, required=True, help='Spectrometer frequency for Nitrogen (MHz)')
  parser.add_argument('--out', default='peaks.tab', help='Output filename (default: peaks.tab)')

  args = parser.parse_args()
  convert_nef_to_tab(args.data, args.sfh, args.sfn, args.out)
  print(f"Converted {args.data} to {args.out}")
