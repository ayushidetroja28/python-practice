import argparse
import json
import sys
from analyzer import analyze_csv

def main(argv=None):
    parser = argparse.ArgumentParser(description="CSV Data Analyzer CLI")
    parser.add_argument("file", help="Path to CSV file (or - for stdin)")
    parser.add_argument("--top", "-t", type=int, default=5, help="Top N categorical values")
    parser.add_argument("--output", "-o", help="Write JSON output to file (defaults to stdout)")
    args = parser.parse_args(argv)


    try:
        if args.file == "-":
            stats = analyze_csv(sys.stdin)
        else:
            stats = analyze_csv(args.file)

        print("------argv-------",stats)
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, default=str)
            print(f"Wrote analysis to {args.output}")
        else:
            print(json.dumps(stats, indent=2, default=str))


    except Exception as e:
        print("Error while analyzing CSV:", e)
        raise

if __name__ == "__main__":
    main()