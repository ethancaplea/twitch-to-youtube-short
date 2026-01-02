import sys

if len(sys.argv) < 2:
    print("No streamer provided")
    sys.exit(1)

streamer = sys.argv[1]
print(f"Received streamer: {streamer}")
