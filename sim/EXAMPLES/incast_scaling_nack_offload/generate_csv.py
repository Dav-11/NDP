#!/usr/bin/env python3
import os
import csv

def parse_dat_file(filepath):
    """
    Parses a space-separated data file where each line has the format:
    conns value
    Returns a list of tuples: (conns, value)
    """
    data = []
    if not os.path.exists(filepath):
        return data
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    conns = int(parts[0])
                    val = float(parts[1])
                    data.append((conns, val))
                except ValueError:
                    continue
    return sorted(data)

def parse_bounces_file(filepath):
    """
    Parses a bounces file where each line has the format:
    conns bounces nacks
    Returns a list of tuples: (conns, bounces, nacks)
    """
    data = []
    if not os.path.exists(filepath):
        return data
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 3:
                try:
                    conns = int(parts[0])
                    bounces = float(parts[1])
                    nacks = float(parts[2])
                    data.append((conns, bounces, nacks))
                except ValueError:
                    continue
    return sorted(data)

def main():
    cwnds = [1, 10, 23]
    missing_files = []
    
    # ----------------------------------------------------
    # 1. Generate incast_sensitivity.csv
    # ----------------------------------------------------
    sensitivity_rows = []
    for cwnd in cwnds:
        filename = f"incast_ndp_completion_times_{cwnd}_270000size_max"
        if not os.path.exists(filename):
            missing_files.append(filename)
            continue
        
        label = f"NDP, IW={cwnd}"
        points = parse_dat_file(filename)
        for conns, max_time in points:
            # Ideal formula matching incast_sensitivity.plot:
            # 100 * max_time / (conns * 271920.0 * 8.0 / 1e10 + 0.000042256) - 100
            ideal_time = conns * 271920.0 * 8.0 / 10000000000.0 + 0.000042256
            y_value = 100.0 * max_time / ideal_time - 100.0
            
            sensitivity_rows.append({
                "label": label,
                "x value (incast flows)": conns,
                "y value": y_value
            })
            
    # ----------------------------------------------------
    # 2. Generate incast_overhead.csv
    # ----------------------------------------------------
    overhead_rows = []
    for cwnd in cwnds:
        filename = f"bounces{cwnd}"
        if not os.path.exists(filename):
            missing_files.append(filename)
            continue
            
        label_bounces = f"RTX (Bounces), IW={cwnd}"
        label_nacks = f"RTX (Nacks), IW={cwnd}"
        
        points = parse_bounces_file(filename)
        for conns, bounces, nacks in points:
            # Formulas matching incast_overhead.plot:
            # bounces / (conns * 30.0) and nacks / (conns * 30.0)
            y_bounces = bounces / (conns * 30.0)
            y_nacks = nacks / (conns * 30.0)
            
            overhead_rows.append({
                "label": label_bounces,
                "x value (incast flows)": conns,
                "y value": y_bounces
            })
            overhead_rows.append({
                "label": label_nacks,
                "x value (incast flows)": conns,
                "y value": y_nacks
            })

    # Print summary of missing files if any
    if missing_files:
        print("Warning: The following expected data files were not found:")
        for f in missing_files:
            print(f"  - {f}")
        print("This is normal if the simulation script (run.sh) is still running or has not been executed yet.")

    headers = ["label", "x value (incast flows)", "y value"]

    # Write sensitivity file if there is data
    if sensitivity_rows:
        sens_file = "incast_sensitivity.csv"
        with open(sens_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(sensitivity_rows)
        print(f"Successfully generated: {os.path.abspath(sens_file)} ({len(sensitivity_rows)} points)")
    else:
        print("No sensitivity data collected. incast_sensitivity.csv not written.")

    # Write overhead file if there is data
    if overhead_rows:
        over_file = "incast_overhead.csv"
        with open(over_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(overhead_rows)
        print(f"Successfully generated: {os.path.abspath(over_file)} ({len(overhead_rows)} points)")
    else:
        print("No overhead data collected. incast_overhead.csv not written.")

if __name__ == "__main__":
    main()
