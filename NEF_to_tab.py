import re
import argparse
import sys

parser = argparse.ArgumentParser(description="Conver NEF peaklists to nmrDraw .tab")
parser.add_argument("--sfn", type=float, required=True, help="15N Spectrometer frequency in MHz")
parser.add_argument("--sfh", type=float, required=True, help="1H Spectrometer frequency in MHz")
parser.add_argument("--data", type=str, required=True, help="NEF file path")

def convert_nef_to_tab(nef_path, sf_h, sf_n):
  try:
    with open(nef_path, 'r') as f:
      content = f.read()
  except FileNotFoundError:
      print(f"Error: File '{nef_path}' not found.")
      sys.exit(1)

  peak_loop_match = re.search(r'loop_\s+(_nef_peak\..*?)\s+stop_', content, re.DOTALL)
  if not peak_loop_match:
    print("Error: Couldn't find _nef_peak loop in the NEF file.")
    return

  lines = peak_loop_match.group(0).splitlines()

  tags = [l.strip() for l in lines if l.strip().startswith('_nef_peak.')]
  data_lines = [l.strip() for l in lines if l.strip() and not l.strip().startswith(('_', 'loop_', 'stop_'))]

  try:
    idx_pos1 = next(i for i, t in enumerate(tags) if 'position_1' in t)
    idx_pos2 = next(i for i, t in enumerate(tags) if 'position_2' in t)
    idx_height = next(i for i, t in enumerate(tags) if 'height' in t)
    idx_id = next(i for i, t in enumerate(tags) if 'peak_id' in t)
    try:
      idx_res_num = next(i for i, t in enumerate(tags) if 'sequence_code_1' in t)
      idx_res_nam = next(i for i, t in enumerate(tags) if 'residue_name_1' in t)
    except StopIteration:
      idx_res_num = idx_res_nam = None
  except StopIteration:
    print("Error: Required NEF tags (position, height, or peak_id) are missing.")
    return

  output_file = nef_path.replace('.nef', '.tab')
  header = [
    "REMARK nmrDraw Peak List",
    "DATA_TYPE 2D_PEAK_LIST",
    "VARS   INDEX ID X_PPM Y_PPM X_HZ Y_HZ HEIGHT DX DY ASSIG",
    "FORMAT %5d %5d %9.3f %9.3f %12.3f %12.3f %15.3e %8.3f %8.3f %s",
  ]

  tab_data = []
  for i, line in enumerate(data_lines):
    parts = line.split()
    if len(parts) < len(tags): continue

    peak_id = int(parts[idx_id])
    ppm_n = float(parts[idx_pos1])
    ppm_h = float(parts[idx_pos2])
    
    height_str = float(parts[idx_height])
    height = float(height_str) if height_str != '.' else 0.0
    
    hz_h = ppm_h * sf_h
    hz_n = ppm_n * sf_n

    assig = "None"
    if idx_res_num is not None and parts[idx_res_num] != '.':
      assig = f"{parts[idx_res_nam]}{parts[idx_res_num]}"

    tab_row = f"{i+1:5d} {peak_id:5d} {ppm_h:9.3f} {ppm_n:9.3f} {hz_h:12.3f} {hz_n:12.3f} {height:15.3e} {0.0:8.3f} {0.0:8.3f} {assig}"
    tab_data.append(tab_row)

  with open(output_file, 'w') as f:
    f.write('\n'.join(header + tab_data))

  print(f"Converted {len(tab_data)} peaks.")
  print(f"Output saved to {output_file}")

if __name__ == "__main__":
  args = parser.parse_args()
  convert_nef_to_tab(args.data, args.sfh, args.sfn)
